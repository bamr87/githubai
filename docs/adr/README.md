<!-- kit: sdlc v0.1.0 · ADR index (UPS-WORK-04, decision D2: law-ai format) -->
# Architecture Decision Records

> The index of githubai's architecture decision records: why each hard-to-reverse choice was made, and the tests that hold it.

This directory records decisions for githubai that are hard to reverse: the stack, data model, security model, public interfaces, and any relaxation of a gate. Add an ADR in the same PR as the change it justifies.

## Format

- File name: `NNNN-short-kebab-title.md`, where `NNNN` is a four-digit sequence (`0001`, `0002`, …). Never renumber; a skipped number stays skipped.
- Start from [`0000-template.md`](0000-template.md).
- Required sections: **Status**, **Context**, **Decision**, **Consequences**, **Alternatives considered**, **Supersedes / Superseded by**.
- Status values: `proposed`, `accepted`, `superseded`, `deprecated`. A superseded ADR is never deleted; it links forward to the ADR that replaced it.

## Index

| ID | Title | Status |
| --- | --- | --- |
| 0001 | [Record architecture decisions](0001-record-architecture-decisions.md) | accepted |
| 0002 | [Routing parity between Actions mode and app mode](0002-relay-routing-parity.md) | accepted |
| 0003 | [Org policy is subtractive and keeps the last document that parsed](0003-subtractive-org-policy.md) | accepted |
| 0004 | [A zero-dependency relay with its own YAML subset parser](0004-zero-dependency-relay.md) | accepted |
| 0005 | [Layered config: base, then profile, then repository](0005-layered-config-merge.md) | accepted |
