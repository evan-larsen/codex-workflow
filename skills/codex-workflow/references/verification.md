# Proportionate verification

Choose evidence according to consequence and uncertainty, not ceremony.
Low-risk, reversible work may need only coherent source and diff inspection.
Critical contracts require the strongest practical evidence available, with
any unavailable boundary reported honestly.

Implementation complexity, branching, or a state machine does not by itself
make a change test-worthy; critical risk still controls whether tests add
enough value to run or create.

No command is required when source and diff inspection are decisive. Existing
unit tests are regression gates, not diagnostic tools: do not run them to find
the cause of a problem. When source cannot distinguish live hypotheses, use
the cheapest targeted observation, log, or reproduction instead.

## Evidence ladder

### Reversible presentation or text

Examples: copy, spacing, color, documentation wording, local declarative data,
or a mechanical rename with no behavioral contract change.

- Review the exact diff.
- Run no command when that review is decisive; otherwise use at most one
  exact-file syntax or formatting check when relevant.
- Do not add tests, run a full typecheck, or start a tester by default.

### Local behavior

Examples: one component interaction, parser branch, localized bug fix, or
contained service behavior.

- Prefer exact diff/source inspection and one cheap static or manual proof.
- Add a regression test only for a critical contract or an important reproduced
  regression with a stable seam.
- Do not run a nearby test by default, run unrelated suites, or repeat a
  passing check.

### Shared behavior or public boundary

Examples: shared types, cross-package interfaces, synchronization, persistence,
progression, or platform-version behavior.

- Prove the changed semantic boundary first.
- Add focused contract or regression coverage when the changed boundary is
  critical or the user explicitly requests it.
- Run typecheck, lint, or a broader package suite only where the shared boundary
  makes it relevant and the check names the cross-cutting critical risk it
  proves.
- Use a tester only when independent executable evidence materially improves
  confidence for a risk-selected package; do not add one for low-risk work.

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

Implement a coherent increment before verifying it. The implementation owner
verifies once. A coordinator or reviewer trusts a clear passing report and does
not rerun it. Do not run formatter, lint, typecheck, and tests after each small
edit. Batch independent checks when they do not share mutable state. Run broad
CI or a full suite once only when a named cross-cutting critical risk warrants
it or the user requests it. A commit does not trigger another check unless the
commit changed files after the last proof.

Formatting is not universal verification. Format only task-owned files and only
with the repository's supported scoped command. Documentation changes are
required only when behavior makes existing docs inaccurate.

An independent tester is for risk-selected packages, not low-risk work, and
returns one grouped report ordered by materiality. Style
preferences and speculative improvements are not defects. After one grouped
repair, recheck the failed criteria and affected regression boundary; do not
restart the entire audit unless the repair invalidated it.
