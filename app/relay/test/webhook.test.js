import assert from "node:assert/strict";
import test from "node:test";

import { POLICY_PATH } from "../src/policy.js";
import { DISPATCH_TYPES } from "../src/routing.js";
import { OUTCOMES, memoryStore } from "../src/store.js";
import { handleWebhook } from "../src/webhook.js";
import {
  fakeGithub,
  issueOpened,
  makeEnv,
  prOpened,
  signedRequest,
  testContext,
} from "./helpers.js";

const POLICY_KEY = `acme/.github/${POLICY_PATH}`;

function setup(options = {}) {
  const store = memoryStore();
  const github = fakeGithub(options.github);
  const ctx = testContext({ store, github, env: options.env || makeEnv() });
  return { ctx, store, github };
}

const lastActivity = async (store, id = 42) => (await store.listActivity([id], 1))[0];

test("rejects an unsigned or wrongly signed delivery before parsing it", async () => {
  const { ctx, store } = setup();
  const bad = signedRequest({ event: "issues", payload: issueOpened(), secret: "wrong-secret" });
  const response = await handleWebhook(bad, ctx);
  assert.equal(response.status, 401);
  assert.equal((await store.listActivity([42], 10)).length, 0, "unverified input must not be recorded");

  const missing = signedRequest({ event: "issues", payload: issueOpened(), signature: "" });
  assert.equal((await handleWebhook(missing, ctx)).status, 401);
});

test("answers ping without touching state", async () => {
  const { ctx, store } = setup();
  const response = await handleWebhook(signedRequest({ event: "ping", payload: { zen: "hi" } }), ctx);
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "pong");
  assert.equal((await store.health()).activity, 0);
});

test("dispatches a new issue to the triage lane", async () => {
  const { ctx, store, github } = setup();
  const response = await handleWebhook(signedRequest({ event: "issues", payload: issueOpened() }), ctx);

  assert.equal(response.status, 202);
  assert.deepEqual(github.dispatches, [
    {
      installationId: 42,
      repo: "acme/api",
      type: DISPATCH_TYPES.triage,
      payload: { issue_number: "7" },
    },
  ]);
  const activity = await lastActivity(store);
  assert.equal(activity.outcome, OUTCOMES.DISPATCHED);
  assert.equal(activity.dispatchType, DISPATCH_TYPES.triage);
  assert.equal(activity.subject, "#7");
  // The repo is learned from traffic even when the installation predates the relay.
  assert.deepEqual((await store.getInstallation(42)).repos, ["acme/api"]);
  assert.equal((await store.getInstallation(42)).accountLogin, "acme");
});

test("a redelivered webhook does not dispatch twice", async () => {
  const { ctx, github } = setup();
  const request = () => signedRequest({ event: "issues", payload: issueOpened(), deliveryId: "d-1" });

  assert.equal((await handleWebhook(request(), ctx)).status, 202);
  const second = await handleWebhook(request(), ctx);
  assert.equal(second.status, 200);
  assert.match(await second.text(), /duplicate/);
  assert.equal(github.dispatches.length, 1);
});

test("records why an event was ignored instead of dropping it", async () => {
  const { ctx, store, github } = setup();
  const payload = issueOpened({ labels: [{ name: "claude:skip" }] });
  const response = await handleWebhook(signedRequest({ event: "issues", payload }), ctx);

  assert.equal(response.status, 200);
  assert.equal(github.dispatches.length, 0);
  const activity = await lastActivity(store);
  assert.equal(activity.outcome, OUTCOMES.IGNORED);
  assert.match(activity.detail, /claude:skip/);
});

test("org policy blocks a lane and the reason is auditable", async () => {
  const { ctx, store, github } = setup({
    github: { files: { [POLICY_KEY]: "automation:\n  auto_merge:\n    enabled: false\n" } },
  });
  const payload = prOpened({ user: { login: "dependabot[bot]" } });
  const response = await handleWebhook(signedRequest({ event: "pull_request", payload }), ctx);

  assert.equal(response.status, 200);
  assert.equal(github.dispatches.length, 0);
  const activity = await lastActivity(store);
  assert.equal(activity.outcome, OUTCOMES.SKIPPED_POLICY);
  assert.match(activity.detail, /automation\.auto_merge/);

  // A lane the policy leaves alone still dispatches.
  const review = await handleWebhook(
    signedRequest({ event: "pull_request", payload: prOpened() }),
    ctx,
  );
  assert.equal(review.status, 202);
  assert.equal(github.dispatches[0].type, DISPATCH_TYPES.review);
});

test("suspended installations route nothing", async () => {
  const { ctx, store, github } = setup();
  await store.upsertInstallation({
    id: 42,
    accountLogin: "acme",
    suspendedAt: "2026-08-01T00:00:00.000Z",
    now: "2026-08-01T00:00:00.000Z",
  });

  const response = await handleWebhook(signedRequest({ event: "issues", payload: issueOpened() }), ctx);
  assert.equal(response.status, 200);
  assert.equal(github.dispatches.length, 0);
  assert.equal((await lastActivity(store)).outcome, OUTCOMES.SUSPENDED);
});

test("rate limiting refuses excess dispatches for one installation only", async () => {
  const { ctx, store, github } = setup({ env: makeEnv({ RATE_LIMIT_PER_MINUTE: "2" }) });
  const fire = (n) =>
    handleWebhook(
      signedRequest({ event: "issues", payload: issueOpened({ number: n }), deliveryId: `d-${n}` }),
      ctx,
    );

  assert.equal((await fire(1)).status, 202);
  assert.equal((await fire(2)).status, 202);
  const limited = await fire(3);
  assert.equal(limited.status, 429);
  assert.equal(github.dispatches.length, 2);
  assert.equal((await lastActivity(store)).outcome, OUTCOMES.RATE_LIMITED);

  // The window rolls over.
  ctx.advance(61_000);
  assert.equal((await fire(4)).status, 202);
});

test("a failed dispatch is reported as an error, not swallowed", async () => {
  const { ctx, store } = setup({ github: { dispatchError: new Error("dispatch failed: 403") } });
  const response = await handleWebhook(signedRequest({ event: "issues", payload: issueOpened() }), ctx);

  assert.equal(response.status, 502);
  const activity = await lastActivity(store);
  assert.equal(activity.outcome, OUTCOMES.ERROR);
  assert.match(activity.detail, /403/);
});

test("a failed dispatch stays redeliverable", async () => {
  // Deduplication must not turn a transient failure into a permanent one: the
  // operator's Redeliver button is the only recovery path GitHub offers.
  const { ctx, github } = setup({ github: { dispatchError: new Error("502 from GitHub") } });
  const request = () => signedRequest({ event: "issues", payload: issueOpened(), deliveryId: "d-1" });

  assert.equal((await handleWebhook(request(), ctx)).status, 502);

  github.dispatchError = null;
  const retry = await handleWebhook(request(), ctx);
  assert.equal(retry.status, 202, "redelivery after a failure must be accepted, not deduplicated");
  assert.equal(github.dispatches.length, 1);
});

test("installation lifecycle events maintain the tenant record", async () => {
  const { ctx, store } = setup();
  const installation = {
    id: 42,
    account: { login: "acme", type: "Organization" },
    target_type: "Organization",
    repository_selection: "selected",
  };

  await handleWebhook(
    signedRequest({
      event: "installation",
      payload: { action: "created", installation, repositories: [{ full_name: "acme/api" }] },
    }),
    ctx,
  );
  let record = await store.getInstallation(42);
  assert.equal(record.accountLogin, "acme");
  assert.deepEqual(record.repos, ["acme/api"]);

  await handleWebhook(
    signedRequest({
      event: "installation_repositories",
      payload: {
        action: "added",
        installation,
        repositories_added: [{ full_name: "acme/web" }],
        repositories_removed: [{ full_name: "acme/api" }],
      },
    }),
    ctx,
  );
  assert.deepEqual((await store.getInstallation(42)).repos, ["acme/web"]);

  await handleWebhook(
    signedRequest({
      event: "installation",
      payload: { action: "suspend", installation: { ...installation, suspended_at: "2026-08-19T00:00:00Z" } },
    }),
    ctx,
  );
  assert.ok((await store.getInstallation(42)).suspendedAt);

  await handleWebhook(
    signedRequest({ event: "installation", payload: { action: "unsuspend", installation } }),
    ctx,
  );
  assert.equal((await store.getInstallation(42)).suspendedAt, null);

  await handleWebhook(
    signedRequest({ event: "installation", payload: { action: "deleted", installation } }),
    ctx,
  );
  assert.equal(await store.getInstallation(42), null, "uninstall must delete the tenant record");
});

test("marketplace purchases update the account's plan", async () => {
  const { ctx, store } = setup();
  await store.upsertInstallation({ id: 42, accountLogin: "acme", now: "2026-08-01T00:00:00.000Z" });

  await handleWebhook(
    signedRequest({
      event: "marketplace_purchase",
      payload: {
        action: "purchased",
        marketplace_purchase: { account: { login: "acme" }, plan: { name: "Team" } },
      },
    }),
    ctx,
  );
  assert.equal((await store.getInstallation(42)).plan, "team");

  await handleWebhook(
    signedRequest({
      event: "marketplace_purchase",
      payload: {
        action: "cancelled",
        marketplace_purchase: { account: { login: "acme" }, plan: { name: "Team" } },
      },
    }),
    ctx,
  );
  assert.equal((await store.getInstallation(42)).plan, "free");
});

test("malformed JSON is rejected after signature verification", async () => {
  const { ctx } = setup();
  const response = await handleWebhook(signedRequest({ event: "issues", payload: "{not json" }), ctx);
  assert.equal(response.status, 400);
});

test("a delivery with no installation is recorded rather than dropped", async () => {
  const { ctx, store } = setup();
  const response = await handleWebhook(
    signedRequest({ event: "issues", payload: { action: "opened", issue: { number: 1, labels: [], user: { type: "User" } } } }),
    ctx,
  );
  assert.equal(response.status, 200);
  const activity = (await store.listActivity([0], 5))[0];
  assert.equal(activity.outcome, OUTCOMES.IGNORED);
  assert.match(activity.detail, /installation/);
});
