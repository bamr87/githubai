# ADR 0004 — A zero-dependency relay with its own YAML subset parser

> The relay is a Cloudflare Worker with no npm dependencies and no build step, so org policy is parsed by the YAML subset in `app/relay/src/yaml.js`, which must keep agreeing with PyYAML.

- **Status**: accepted
- **Date**: 2026-08-19
- **Deciders**: the maintainer (bamr87); recorded after the fact on 2026-11-15 from the shipped code and docs (#137)
- **Related**: #110 (hosted multi-tenant relay); constitution § 2; [app/README.md](../../app/README.md); [`app/relay/src/yaml.js`](../../app/relay/src/yaml.js); tests `tests/test_app.py::test_relay_has_no_dependencies`, `tests/test_app.py::test_relay_yaml_parser_agrees_with_pyyaml` and `app/relay/test/yaml.test.js`

## Context

The relay in `app/relay/` is the one real program in GitHubAI: a router, not a runtime, and the one component no repository dogfoods, so it is tested behaviourally against the same modules the Worker imports. Org policy has to be YAML, because it is the same `githubai.yml` schema repositories already use and a second format would break "config over code". Parsing YAML in the Worker would normally mean a library.

## Decision

The relay has no `dependencies` or `devDependencies` in `app/relay/package.json`, no build step, and `npm test` runs `node --test`; the Worker runs `src/` as written. Org policy is therefore parsed by `src/yaml.js`, a deliberately small YAML subset: block and flow mappings and sequences, quoted and plain scalars, block scalars, comments, and a single leading `---`. It throws `YamlError` on anything it cannot represent faithfully (anchors, aliases, merge keys, explicit tags, multi-document streams and tab indentation), and it follows PyYAML's YAML 1.1 booleans so a file means the same thing in the relay and in `actions/load-config`. `tests/test_app.py::test_relay_has_no_dependencies` holds the first rule; `tests/test_app.py::test_relay_yaml_parser_agrees_with_pyyaml` and `app/relay/test/yaml.test.js` parse this repository's real config files with both parsers and require the same result.

## Consequences

**Positive**

- The Worker ships exactly the code in `src/`, and its tests run on plain Node 20+ against the same modules, with nothing to install and no Cloudflare account.
- A construct the parser cannot represent faithfully fails loudly instead of being misread, and the agreement test keeps the supported subset in step with what `actions/load-config` reads.

**Negative**

- The parser is code this repository owns and must keep in step with PyYAML.
- A policy file that uses an unsupported construct is rejected rather than read, so under [ADR 0003](0003-subtractive-org-policy.md) the last good policy keeps applying until the file is fixed.

## Alternatives considered

- **A YAML library in the Worker** — it would end the relay's zero-dependency rule that this ADR records.
- **A policy format other than YAML** — forcing operators to learn a second format would violate "config over code".
- **Best-effort parsing of unsupported constructs** — a policy document that parses to the wrong thing is worse than one that fails loudly.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
