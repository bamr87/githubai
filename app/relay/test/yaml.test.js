import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { YamlError, parseYaml } from "../src/yaml.js";

const repoRoot = fileURLToPath(new URL("../../../", import.meta.url));

test("parses the org policy shape", () => {
  const doc = parseYaml(`
version: 1
org:
  enabled: true
  repos:
    include: ["*"]
    exclude:
      - legacy-*
automation:
  triage: {enabled: true}
  auto_merge:
    enabled: false
`);
  assert.deepEqual(doc, {
    version: 1,
    org: { enabled: true, repos: { include: ["*"], exclude: ["legacy-*"] } },
    automation: { triage: { enabled: true }, auto_merge: { enabled: false } },
  });
});

test("handles comments, quotes, nulls, numbers and YAML 1.1 booleans", () => {
  const doc = parseYaml(`
# leading comment
a: yes      # trailing comment
b: 'off'
c: "quoted # not a comment"
d:
e: ~
f: -12
g: 1.5
h: on
`);
  assert.deepEqual(doc, {
    a: true,
    b: "off",
    c: "quoted # not a comment",
    d: null,
    e: null,
    f: -12,
    g: 1.5,
    h: true,
  });
});

test("parses sequences of mappings", () => {
  const doc = parseYaml(`
taxonomy:
  - name: "type:bug"
    color: d73a4a
  - name: "type:docs"
    color: 0075ca
`);
  assert.deepEqual(doc.taxonomy, [
    { name: "type:bug", color: "d73a4a" },
    { name: "type:docs", color: "0075ca" },
  ]);
});

test("parses literal and folded block scalars with chomping", () => {
  const doc = parseYaml(`
literal: |
  one
  two
folded: >-
  a
  b

  c
`);
  assert.equal(doc.literal, "one\ntwo\n");
  assert.equal(doc.folded, "a b\n\nc");
});

test("rejects constructs it cannot represent faithfully", () => {
  const cases = [
    ["anchors", "a: &anchor value"],
    ["aliases", "a: *anchor"],
    ["tags", "a: !!str 5"],
    ["merge keys", "a:\n  <<: b"],
    ["tab indentation", "a:\n\tb: 1"],
    ["duplicate keys", "a: 1\na: 2"],
    ["multi-document", "a: 1\n---\nb: 2"],
  ];
  for (const [label, source] of cases) {
    assert.throws(() => parseYaml(source), YamlError, `${label} must be rejected`);
  }
});

// The whole point of this parser is that a githubai.yml means the same thing
// here as it does in actions/load-config; fixtures are the real repo configs.
test("agrees with the framework's own config files", () => {
  for (const file of [
    "profiles/_base.yml",
    "profiles/library.yml",
    "template/githubai.yml",
    ".github/githubai.yml",
  ]) {
    const doc = parseYaml(readFileSync(repoRoot + file, "utf8"));
    assert.equal(typeof doc, "object", `${file} must parse to a mapping`);
    assert.ok(doc.version === 1 || doc.repo || doc.profile, `${file} parsed to something unexpected`);
  }
  const base = parseYaml(readFileSync(repoRoot + "profiles/_base.yml", "utf8"));
  assert.equal(base.automation.auto_merge.enabled, false);
  assert.equal(base.automation.auto_merge.max_risk, "low");
  assert.deepEqual(base.automation.auto_merge.allowed_authors, ["dependabot[bot]", "renovate[bot]"]);
  assert.equal(base.labels.taxonomy.length, 18);
  assert.ok(base.profile.guidance.startsWith("General standards"));
});
