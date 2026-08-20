import assert from "node:assert/strict";
import test from "node:test";

import { OUTCOMES, d1Store, memoryStore, retentionCutoff } from "../src/store.js";

const NOW = "2026-08-19T12:00:00.000Z";

test("delivery ids are claimed exactly once", async () => {
  const store = memoryStore();
  assert.equal(await store.claimDelivery("d-1", NOW), true);
  assert.equal(await store.claimDelivery("d-1", NOW), false);
  assert.equal(await store.claimDelivery("d-2", NOW), true);
  // A delivery with no id (hand-crafted request) is always allowed through.
  assert.equal(await store.claimDelivery("", NOW), true);
  assert.equal(await store.claimDelivery("", NOW), true);
});

test("a released delivery can be claimed again", async () => {
  const store = memoryStore();
  await store.claimDelivery("d-1", NOW);
  await store.releaseDelivery("d-1");
  assert.equal(await store.claimDelivery("d-1", NOW), true);
});

test("d1 tells a key conflict apart from a database failure", async () => {
  // Treating every insert error as "already seen" would silently drop every
  // event during an outage, so only a constraint violation may mean duplicate.
  const failing = (error) =>
    d1Store({ prepare: () => ({ bind: () => ({ run: async () => { throw error; } }) }) });

  const conflict = failing(new Error("D1_ERROR: UNIQUE constraint failed: deliveries.delivery_id"));
  assert.equal(await conflict.claimDelivery("d-1", NOW), false);

  const outage = failing(new Error("D1_ERROR: network error"));
  await assert.rejects(() => outage.claimDelivery("d-1", NOW), /network error/);
});

test("installation records carry their repositories and survive updates", async () => {
  const store = memoryStore();
  await store.upsertInstallation({ id: 42, accountLogin: "acme", now: NOW });
  await store.addRepos(42, ["acme/api", "acme/web"], NOW);
  await store.addRepos(42, ["acme/api"], NOW);

  let installation = await store.getInstallation(42);
  assert.deepEqual(installation.repos, ["acme/api", "acme/web"]);
  assert.equal(installation.plan, "free");
  assert.equal(installation.createdAt, NOW);

  await store.removeRepos(42, ["acme/web"]);
  await store.upsertInstallation({ id: 42, accountLogin: "acme", now: "2026-08-20T00:00:00.000Z" });
  installation = await store.getInstallation(42);
  assert.deepEqual(installation.repos, ["acme/api"]);
  assert.equal(installation.createdAt, NOW, "createdAt must not be overwritten by an update");
  assert.equal(installation.updatedAt, "2026-08-20T00:00:00.000Z");
});

test("uninstalling removes every trace of the tenant", async () => {
  const store = memoryStore();
  await store.upsertInstallation({ id: 42, accountLogin: "acme", now: NOW });
  await store.addRepos(42, ["acme/api"], NOW);
  await store.setPolicy(42, { source: "s", document: { enabled: true }, fetchedAt: NOW });
  await store.bumpRate(42, 1, 60);

  await store.deleteInstallation(42);
  assert.equal(await store.getInstallation(42), null);
  assert.equal(await store.getPolicy(42), null);
  assert.deepEqual(await store.listInstallations([42]), []);
});

test("plan changes apply to every installation of an account", async () => {
  const store = memoryStore();
  await store.upsertInstallation({ id: 1, accountLogin: "acme", now: NOW });
  await store.upsertInstallation({ id: 2, accountLogin: "other", now: NOW });
  await store.setPlan("acme", "team", NOW);
  assert.equal((await store.getInstallation(1)).plan, "team");
  assert.equal((await store.getInstallation(2)).plan, "free");

  // A later installation for the same account inherits the recorded plan.
  await store.upsertInstallation({ id: 3, accountLogin: "acme", now: NOW });
  assert.equal((await store.getInstallation(3)).plan, "team");
});

test("activity is per-installation, newest first, and never leaks across tenants", async () => {
  const store = memoryStore();
  for (const [id, repo] of [[1, "a/one"], [2, "b/two"], [1, "a/three"]]) {
    await store.recordActivity({
      installationId: id,
      repo,
      event: "issues",
      outcome: OUTCOMES.DISPATCHED,
      now: NOW,
    });
  }
  const mine = await store.listActivity([1], 10);
  assert.deepEqual(mine.map((row) => row.repo), ["a/three", "a/one"]);
  assert.equal((await store.listActivity([2], 10)).length, 1);
  assert.equal((await store.listActivity([], 10)).length, 0);
  assert.equal((await store.listActivity([1], 1)).length, 1);
});

test("rate limiting counts within a window and resets on the next one", async () => {
  const store = memoryStore();
  assert.deepEqual(await store.bumpRate(42, 100, 2), { count: 1, allowed: true });
  assert.deepEqual(await store.bumpRate(42, 100, 2), { count: 2, allowed: true });
  assert.deepEqual(await store.bumpRate(42, 100, 2), { count: 3, allowed: false });
  assert.deepEqual(await store.bumpRate(42, 101, 2), { count: 1, allowed: true });
  // Counters are per installation.
  assert.deepEqual(await store.bumpRate(43, 101, 2), { count: 1, allowed: true });
});

test("pruning drops aged activity and delivery ids", async () => {
  const store = memoryStore();
  await store.recordActivity({ installationId: 1, outcome: OUTCOMES.IGNORED, event: "issues", now: "2026-06-01T00:00:00.000Z" });
  await store.recordActivity({ installationId: 1, outcome: OUTCOMES.IGNORED, event: "issues", now: NOW });
  await store.claimDelivery("old", "2026-06-01T00:00:00.000Z");

  await store.prune(retentionCutoff(Date.parse(NOW)));
  assert.equal((await store.listActivity([1], 10)).length, 1);
  assert.equal(await store.claimDelivery("old", NOW), true, "pruned ids are claimable again");
});

test("retentionCutoff is 30 days back by default", () => {
  const cutoff = retentionCutoff(Date.parse("2026-08-19T12:00:00Z"));
  assert.equal(cutoff, "2026-07-20T12:00:00.000Z");
  assert.equal(retentionCutoff(Date.parse("2026-08-19T12:00:00Z"), 1), "2026-08-18T12:00:00.000Z");
});
