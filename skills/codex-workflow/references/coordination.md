# Coordination for larger work

Read this reference only when the outcome needs multiple workers or several
implementation and verification waves.

## Build the critical path once

Identify the smallest set of independent ownership packages and the dependency
edges between them. Dispatch ready packages together. Do not serialize work
that can safely proceed in parallel, and do not fragment tightly coupled code
merely to increase worker count.

Routine repository discovery belongs to the implementer that needs it. Do not
place an investigator in front of implementation unless a named uncertainty
actually blocks the implementation boundary. When an uncertainty can be
resolved alongside independent implementation, run it concurrently.

Use one implementation owner for each mutable surface and name one integration
owner when a behavior spans packages. Shared documentation has one edit owner.
Other workers return verified facts instead of making overlapping edits.

## Avoid coordinator traffic

Do not create Companion. Workers report directly to the main coordinator. The
coordinator processes all reports available at a lifecycle wake in one turn.
It does not forward every report to another agent, acknowledge delivery, or act
as a proxy between an executor and tester.

Pair a tester with the responsible executor. The tester sends one prioritized,
deduplicated defect packet directly to that executor. The executor performs one
grouped repair pass and returns focused evidence. The tester performs one
focused recheck. A second repair cycle is justified only by a remaining
material failure; otherwise report residual risk and finish.

## Reuse context

Continue the existing worker for repairs and adjacent follow-ups within its
ownership. A follow-up contains only the task ID, changed requirement or state,
new evidence, affected acceptance criterion, and next action. Never resend the
original prompt or ask for a fresh inventory.

Replace a worker only after one evidence-oriented retry fails, its context is
materially stale or confused, or independent judgment is required.

## Default tool budgets

These budgets are latency controls, not permission to omit necessary work. A
worker may exceed one only when a failure or new fact changes the task boundary,
and it must state that reason in its terminal report.

- Investigator: normally at most 6 outer tool calls.
- Micro implementation: normally 4 outer calls—inspect, edit, verify, plus one
  adaptive call only if evidence changes the seam.
- Bounded implementation package: normally at most 12 outer tool calls. Batch
  known reads, multi-file patches, and independent checks.
- Auditor or tester: normally at most 8 outer tool calls and one grouped finding
  packet.
- Senior executor: normally at most 16 outer tool calls for its hard slice.

Do not spend calls on repeated file inventories, whole-document reads after the
decisive section is known, one-command-at-a-time checking, or re-reading source
that has not changed. Before each additional discovery call, identify the fact
that could change the next action. If none exists, implement or conclude.

## Long-task execution

Use this sequence once per coherent outcome:

1. Make one decomposition and acceptance decision.
2. Dispatch all ready independent packages.
3. Wait once for lifecycle events instead of polling.
4. Integrate reports and issue at most one grouped implementation or repair
   wave per affected owner.
5. Run the selected verification boundary once after the coherent change.
6. Broaden or repeat only for a failure, new change, or unresolved material
   concern.

An eight-hour worker can be appropriate for a genuinely indivisible release or
migration. Duration alone is not a failure. Excessive sequential discovery,
duplicated context loading, repeated full checks, and one-defect-per-turn repair
loops are failures even when the task is large.
