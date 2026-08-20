import assert from "node:assert/strict";
import test from "node:test";

import {
  ERROR_POLICY_TTL_SECONDS,
  POLICY_PATH,
  evaluatePolicy,
  globMatch,
  loadPolicy,
  normalizePolicy,
} from "../src/policy.js";
import { DISPATCH_TYPES } from "../src/routing.js";
import { parseYaml } from "../src/yaml.js";
import { fakeGithub, testContext } from "./helpers.js";

const INSTALLATION = { id: 42, accountLogin: "acme" };
const POLICY_KEY = `acme/.github/${POLICY_PATH}`;

const policyOf = (yaml) => normalizePolicy(parseYaml(yaml));

test("no policy document means no restrictions", () => {
  assert.equal(normalizePolicy(null), null);
  assert.deepEqual(evaluatePolicy(null, { repo: "acme/api", dispatchType: DISPATCH_TYPES.triage }), {
    allowed: true,
  });
});

test("org.enabled false stops all routing", () => {
  const policy = policyOf("org:\n  enabled: false\n");
  const verdict = evaluatePolicy(policy, { repo: "acme/api", dispatchType: DISPATCH_TYPES.triage });
  assert.equal(verdict.allowed, false);
  assert.match(verdict.reason, /org\.enabled/);
});

test("automation areas gate their dispatch types and nothing else", () => {
  const policy = policyOf("automation:\n  auto_merge:\n    enabled: false\n");
  assert.equal(
    evaluatePolicy(policy, { repo: "acme/api", dispatchType: DISPATCH_TYPES.autoMerge }).allowed,
    false,
  );
  assert.equal(
    evaluatePolicy(policy, { repo: "acme/api", dispatchType: DISPATCH_TYPES.review }).allowed,
    true,
  );
});

test("include and exclude globs match owner/name and bare name", () => {
  const policy = policyOf(`
org:
  repos:
    include: ["acme/*"]
    exclude: ["legacy-*", "acme/sandbox"]
`);
  const check = (repo) =>
    evaluatePolicy(policy, { repo, dispatchType: DISPATCH_TYPES.triage }).allowed;
  assert.equal(check("acme/api"), true);
  assert.equal(check("acme/legacy-tools"), false);
  assert.equal(check("acme/sandbox"), false);
  assert.equal(check("other/api"), false);

  assert.ok(globMatch("*", "acme/api", "api"));
  assert.ok(globMatch("api", "acme/api", "api"));
  assert.ok(globMatch("acme/a?i", "acme/api", "api"));
  assert.ok(!globMatch("web", "acme/api", "api"));
});

test("policy is subtractive: enabled: true never forces a lane on", () => {
  // Nothing in the policy schema can produce allowed:true for a dispatch the
  // relay did not already decide to send; policy only ever removes.
  const policy = policyOf("automation:\n  auto_merge:\n    enabled: true\n");
  assert.deepEqual(evaluatePolicy(policy, { repo: "a/b", dispatchType: DISPATCH_TYPES.autoMerge }), {
    allowed: true,
  });
  assert.equal(policy.automation.auto_merge, true);
});

test("loadPolicy fetches, then serves from cache until the TTL expires", async () => {
  const github = fakeGithub({ files: { [POLICY_KEY]: "org:\n  enabled: false\n" } });
  const ctx = testContext({ github, ttlSeconds: 300 });

  const first = await loadPolicy(ctx, INSTALLATION);
  assert.equal(first.cached, false);
  assert.equal(first.document.enabled, false);

  github.files = {};
  const second = await loadPolicy(ctx, INSTALLATION);
  assert.equal(second.cached, true);
  assert.equal(second.document.enabled, false);

  ctx.advance(301_000);
  const third = await loadPolicy(ctx, INSTALLATION);
  assert.equal(third.cached, false);
  assert.equal(third.document, null, "file removed upstream means no restrictions");
});

test("a broken policy keeps the last good document instead of failing open", async () => {
  const files = { [POLICY_KEY]: "org:\n  enabled: false\n" };
  const github = fakeGithub({ files });
  const ctx = testContext({ github, ttlSeconds: 300 });

  await loadPolicy(ctx, INSTALLATION);

  files[POLICY_KEY] = "org:\n\tenabled: false\n"; // tab indentation: unparseable
  ctx.advance(301_000);
  const broken = await loadPolicy(ctx, INSTALLATION);
  assert.match(broken.error, /tab/);
  assert.equal(broken.document.enabled, false, "last good policy must still apply");
  assert.equal(
    evaluatePolicy(broken.document, { repo: "acme/api", dispatchType: DISPATCH_TYPES.triage }).allowed,
    false,
  );

  // Errors are retried sooner than the normal TTL so a fix takes effect fast.
  ctx.advance((ERROR_POLICY_TTL_SECONDS + 1) * 1000);
  files[POLICY_KEY] = "org:\n  enabled: true\n";
  const fixed = await loadPolicy(ctx, INSTALLATION);
  assert.equal(fixed.error, "");
  assert.equal(fixed.document.enabled, true);
});

test("an unreadable policy on a first-ever fetch means no restrictions", async () => {
  const github = fakeGithub({ readError: new Error("403 from GitHub") });
  const ctx = testContext({ github });
  const result = await loadPolicy(ctx, INSTALLATION);
  assert.match(result.error, /403/);
  assert.equal(result.document, null);
});

test("a non-mapping policy document is an error, not a silent pass", async () => {
  const github = fakeGithub({ files: { [POLICY_KEY]: "- just\n- a list\n" } });
  const ctx = testContext({ github });
  const result = await loadPolicy(ctx, INSTALLATION);
  assert.match(result.error, /mapping/);
});
