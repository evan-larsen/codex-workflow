# Proportionate verification

Choose the smallest evidence that proves the changed behavior. Verification is
risk-based; it is not a fixed completion ceremony.

## Evidence ladder

### Reversible presentation or text

Examples: copy, spacing, color, documentation wording, local declarative data,
or a mechanical rename with no behavioral contract change.

- Review the exact diff.
- Run exact-file syntax or formatting only when relevant.
- Do not add tests, run a full typecheck, or start a tester by default.

### Local behavior

Examples: one component interaction, parser branch, localized bug fix, or
contained service behavior.

- Run the nearest focused test or one narrow static check.
- Add a regression test only when a stable seam protects meaningful behavior.
- Do not run unrelated suites or repeat a passing check.

### Shared behavior or public boundary

Examples: shared types, cross-package interfaces, synchronization, persistence,
progression, or platform-version behavior.

- Prove the changed semantic boundary first.
- Add focused contract or regression coverage.
- Run typecheck, lint, or a broader package suite only where the shared boundary
  makes it relevant.
- Use a tester when independent executable evidence materially improves
  confidence.

### High-risk operations

Examples: authentication, security, payments, migrations, release or deployment
safety, native registration, irreversible state, or a broad difficult-to-replay
regression.

- Define the acceptance matrix before implementation.
- Use focused boundary proof plus the justified broader gate.
- Record uncompiled native code, untested environments, and manual or provider
  behavior as missing proof.
- Require explicit authorization for external or destructive validation.

## Execution rules

Implement a coherent increment before testing it. Do not run formatter, lint,
typecheck, and tests after each small edit. Batch independent checks when they
do not share mutable state. Run broad CI or a full suite once, only when the
changed surface or user request warrants it.

Formatting is not universal verification. Format only task-owned files and only
with the repository's supported scoped command. Documentation changes are
required only when behavior makes existing docs inaccurate.

An independent tester returns one grouped report ordered by materiality. Style
preferences and speculative improvements are not defects. After one grouped
repair, recheck the failed criteria and affected regression boundary; do not
restart the entire audit unless the repair invalidated it.
