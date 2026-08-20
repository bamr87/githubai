import assert from "node:assert/strict";
import test from "node:test";

import {
  DISPATCH_AREA,
  DISPATCH_TYPES,
  installationRecord,
  lifecycleFor,
  mapEvent,
} from "../src/routing.js";
import { issueOpened, prOpened } from "./helpers.js";

test("routes new human issues to triage", () => {
  const decision = mapEvent("issues", issueOpened());
  assert.deepEqual(decision, {
    type: DISPATCH_TYPES.triage,
    payload: { issue_number: "7" },
    subject: "#7",
  });
});

test("routes the implement label to the implement lane", () => {
  const payload = { ...issueOpened(), action: "labeled", label: { name: "claude:implement" } };
  assert.equal(mapEvent("issues", payload).type, DISPATCH_TYPES.implement);
});

test("mirrors Actions-mode gating that repository_dispatch cannot re-check", () => {
  // claude:skip is checked in each workflow's `if` for direct events; over
  // repository_dispatch there is no issue in the context, so it must be here.
  const skipped = mapEvent("issues", issueOpened({ labels: [{ name: "claude:skip" }] }));
  assert.match(skipped.ignored, /claude:skip/);

  const bot = mapEvent("issues", issueOpened({ user: { type: "Bot" } }));
  assert.match(bot.ignored, /bot/);

  const draft = mapEvent("pull_request", prOpened({ draft: true }));
  assert.match(draft.ignored, /draft/);

  const fork = mapEvent("pull_request", prOpened({ head: { repo: { full_name: "fork/api" } } }));
  assert.match(fork.ignored, /fork/);

  const skippedPr = mapEvent("pull_request", prOpened({ labels: [{ name: "claude:skip" }] }));
  assert.match(skippedPr.ignored, /claude:skip/);
});

test("sends trusted bot PRs to auto-merge and everything else to review", () => {
  assert.equal(
    mapEvent("pull_request", prOpened({ user: { login: "dependabot[bot]" } })).type,
    DISPATCH_TYPES.autoMerge,
  );
  assert.equal(
    mapEvent("pull_request", prOpened({ user: { login: "renovate[bot]" } })).type,
    DISPATCH_TYPES.autoMerge,
  );
  assert.equal(mapEvent("pull_request", prOpened()).type, DISPATCH_TYPES.review);

  // ready_for_review is a human action, so it reviews even for a bot-authored PR.
  const ready = { ...prOpened({ user: { login: "dependabot[bot]" } }), action: "ready_for_review" };
  assert.equal(mapEvent("pull_request", ready).type, DISPATCH_TYPES.review);
});

test("routes PR labels", () => {
  const labeled = (name) => ({ ...prOpened(), action: "labeled", label: { name } });
  assert.equal(mapEvent("pull_request", labeled("claude:auto-merge")).type, DISPATCH_TYPES.autoMerge);
  assert.equal(mapEvent("pull_request", labeled("claude:review")).type, DISPATCH_TYPES.review);
  assert.ok(mapEvent("pull_request", labeled("type:bug")).ignored);
});

test("every unrouted event yields a reason instead of null", () => {
  for (const [event, payload] of [
    ["issue_comment", { action: "created" }],
    ["push", {}],
    ["issues", { action: "closed", issue: { number: 1, labels: [] } }],
  ]) {
    const decision = mapEvent(event, payload);
    assert.ok(decision.ignored, `${event} should be ignored with a reason`);
    assert.equal(typeof decision.ignored, "string");
  }
});

test("every dispatch type maps to an automation area policy can gate", () => {
  for (const type of Object.values(DISPATCH_TYPES)) {
    assert.ok(DISPATCH_AREA[type], `${type} has no automation area`);
  }
});

test("reads installation lifecycle from webhooks", () => {
  const installation = {
    id: 42,
    account: { login: "acme", type: "Organization" },
    target_type: "Organization",
    repository_selection: "all",
  };
  assert.deepEqual(
    lifecycleFor("installation", {
      action: "created",
      installation,
      repositories: [{ full_name: "acme/api" }],
    }),
    { kind: "installed", repos: ["acme/api"] },
  );
  assert.equal(lifecycleFor("installation", { action: "deleted", installation }).kind, "uninstalled");
  assert.equal(lifecycleFor("installation", { action: "unsuspend", installation }).kind, "unsuspended");
  assert.deepEqual(
    lifecycleFor("installation_repositories", {
      action: "added",
      installation,
      repositories_added: [{ full_name: "acme/web" }],
      repositories_removed: [],
    }),
    { kind: "repos-changed", added: ["acme/web"], removed: [] },
  );
  assert.deepEqual(
    lifecycleFor("marketplace_purchase", {
      action: "purchased",
      marketplace_purchase: { account: { login: "acme" }, plan: { name: "Team Plan" } },
    }),
    { kind: "plan-changed", account: "acme", plan: "team-plan" },
  );
  assert.equal(
    lifecycleFor("marketplace_purchase", {
      action: "cancelled",
      marketplace_purchase: { account: { login: "acme" }, plan: { name: "Team Plan" } },
    }).plan,
    "free",
  );
  assert.equal(lifecycleFor("issues", issueOpened()), null);

  assert.deepEqual(installationRecord({ installation }), {
    id: 42,
    accountLogin: "acme",
    accountType: "Organization",
    targetType: "Organization",
    repositorySelection: "all",
    suspendedAt: null,
  });
});
