# Heavy Route

Use after Heavy is selected under `AGENTS.md`.

## Eligibility Gate

Heavy orchestration requires the session's currently selected main agent to be
`gpt-6-astra`, `gpt-5.6-sol`, or `gpt-5.6-terra` with subagent support
available. Do not pin or change that model in worker or route definitions. If
the selected main agent is ineligible or its subagent support is unavailable,
stop before initializing a worker and ask the user to switch the current
session to Astra, Sol, or Terra.

## Heavy Is Delegation-First

Heavy is the worker-led route. The main agent is the coordinator and decision
authority, not the routine investigator, implementer, tester, CI operator, or
documentation editor. If the user wants the selected main model to perform
planning, implementation, and verification itself, use Medium instead.

The main agent owns:

- user intent, scope, acceptance boundaries, and official status;
- package decomposition, mutable ownership, dependency order, and worker
  topology;
- cross-package architecture and public-contract decisions;
- approval of a causal model when a production fix depends on one;
- material escalations, integration judgment, and final claims; and
- user communication.

Workers own operational context and execution. Investigators trace bounded
evidence lanes. Executors own package-local discovery, design, implementation,
focused regression tests, self-check, diff review, and routine repair. Testers
own independent verification when risk warrants it. Companion retains and
reconciles complex operational context. Doc-writers own assigned durable
documentation.

Owning a decision does not require the main agent to recreate the work behind
it. The coordinator should decide from concise evidence and exact references,
opening only the decisive source or artifact needed for a material judgment.
It must not routinely replay discovery, reread complete diffs, rerun passing
checks, or independently derive an implementation sequence already owned by a
worker.

Before a repository tool call, ask whether an available worker can own the
operation. Delegate broad search, execution-path tracing, dependency research,
implementation, tests, lint, formatting, typecheck, builds, log analysis,
environment recovery, and ordinary documentation. A main-agent tool call must
support a coordinator-reserved decision rather than replace worker execution.

The direct Heavy path is limited to conversation, routing, a one-shot metadata
check, or another read-only action whose result can be obtained without
investigation. Any production, test, documentation, configuration, or other
workspace mutation uses an appropriate worker, even when the change is small.
A small Heavy task normally uses one executor; it does not require the full
worker topology.

The main agent alone owns worker topology. Every non-coordinator role MUST NOT
spawn, allocate, delegate to, or create agents or subagents.

## Smallest Sufficient Topology

Use the fewest workers that completely own the outcome:

- Known, bounded implementation: one `default_executor`.
- Ambiguous issue with one decision-relevant uncertainty: one `investigator`,
  then one executor after the main agent approves the fix boundary.
- Multiple independent evidence lanes or multiple worker reports that need
  reconciliation: initialize or reuse Companion and register one coherent
  batch.
- Independent verification: add one `tester` only when the risk gate below is
  satisfied.
- One bounded slice with intrinsically difficult mathematical, logical,
  integration, or cross-cutting reasoning: at most one `senior_executor`.
- Package-local product or technical documentation stays with its executor.
  Use one `doc-writer` only for substantial independently owned or cross-package
  documentation after the relevant behavior is verified.

Before adding a support role, name the specific uncertainty, independent
ownership, or context pressure it removes. Do not create investigators,
Companion, a tester, or a doc-writer merely because Heavy was selected or the
deployment has multiple stages.

Companion is conditional, not ceremonial. Use it for multiple workers,
unfamiliar peripheral context, long-running deployment context, conflicting
evidence, or a coherent report batch. A single executor with a concise terminal
report returns directly to the main agent.

## Investigation and Root-Cause Approval

For a serious or ambiguous issue with independent search lanes, follow
`investigation_team.md`. The main agent supplies the user requirement,
acceptance boundary, known constraints, exact starting references, and the
decision that the evidence must support. Investigators and Companion perform
the source, dependency, log, external, and artifact discovery.

The main agent reviews the resulting brief and exact references, resolves only
material conflicts, and records whether the causal model is confirmed,
probable, or unresolved. It may inspect the smallest decisive source or evidence
needed to approve the fix boundary. Do not begin a production fix until the
main agent can state the affected contract, fix boundary, residual uncertainty,
and acceptance test. This is an approval gate, not a requirement to repeat the
investigation.

Skip an investigation wave when the root cause or implementation boundary is
already established. Send the known outcome directly to an executor.

## Packages and Knowledge Distribution

Delegate bounded, independently completable packages sized for one executor to
own package-local discovery, design, implementation, focused tests, self-check,
and routine repair without carrying feature-wide operational context. Run
packages concurrently only when outcomes and mutable ownership are independent.

Before dispatch, identify the package's primary invariant or closely related
goal, coherent ownership surface, and validation ladder. A broad feature with
separable ownership domains or materially different validation ladders requires
multiple packages, normally assigned to Luna high Fast executors. Do not keep an
end-to-end feature or release in one executor merely because its parts share a
user outcome. Do not split tightly coupled implementation merely to increase
worker count.

File ownership is not behavioral independence. When one user-visible invariant
spans packages, platforms, or React/TypeScript/native layers, name one behavior
owner for the complete invariant or one final integration owner for its full
lifecycle. Package workers prove their assigned part; the integration owner
reconciles the combined behavior. Give each shared or cross-package document one
edit owner; other workers provide verified facts instead of overlapping edits.

Breadth, duration, file count, or context pressure does not make work senior.
Use `senior_executor` only for the smallest bounded slice whose intrinsic
reasoning difficulty exceeds the normal executor lane. It may own difficult
implementation, integration reasoning, or rescue of that slice, but it must not
become a second coordinator or the default owner of all adjacent work.
Before dispatch, state why a Luna high executor cannot safely own the slice and
what specific xhigh reasoning contribution is required. Large files, native
code, cross-layer scope, or a long task are not sufficient by themselves.

Every initial worker uses `fork_turns="none"`. A dispatch envelope contains only:

- task ID and desired outcome;
- ownership, edit surface, and protected areas;
- exact starting references and known upstream decisions;
- relevant interfaces, invariants, compatibility requirements, and authorized
  contract changes;
- acceptance and proportionate verification boundaries;
- for platform/version-gated behavior, a lifecycle matrix covering applicable
  `create | activate | edit | dismiss | cancel | failed interaction | repeat`
  transitions, the APIs that must remain gated, and required proof in each
  environment;
- exact catalog paths for required skills; workers never guess skill paths;
- explicit non-goals and escalation conditions; and
- return routing, including a Companion batch ID when applicable.

This is an outcome capsule, not a coordinator-authored implementation script.
Do not require an ordered Execution Guide, enumerate helpers or branches, or
pre-solve package-local design. The executor chooses files, seams, tests, and
implementation order from repository evidence. Give `senior_executor` only the
hard slice's unresolved decision context and constraints without prescribing
its solution.

Keep envelopes and follow-ups concise through exact references and omission of
irrelevant history. A follow-up contains only the task ID and iteration,
changed state or scope, new evidence, affected criterion, updated guidance, and
next action.

## Verification Risk Gate

The executor owns focused regression tests, package-level validation, and final
diff review by default. Add an independent `tester` when one or more of these is
material:

- persistence, migrations, synchronization, concurrency, authentication,
  security, payments, privacy, or release safety;
- progression, rewards, duplicate-event prevention, or another correctness-
  sensitive domain contract;
- a public or cross-package interface change;
- a broad regression surface or difficult failure reproduction;
- substantial unresolved uncertainty after executor self-check; or
- an explicit user request for independent verification.

Do not create a tester for routine copy, styling, mechanical refactors, trivial
wiring, or a low-risk bounded change whose observable contract is adequately
proved by executor-owned checks.

A tester receives the acceptance matrix, risks, public contracts, regression
boundaries, independence requirements, implementation/evidence references, and
the responsible executor's canonical task name. Start it after executor
self-check unless separate test research is genuinely independent.

Verification proves the changed semantic boundary before broad suites. A broad
CI pass does not replace platform/version gate review, lifecycle-transition
evidence, or another changed-boundary proof. Run broader checks only when shared
contracts or regression risk justify them.

## Repair and Escalation

When a tester is assigned, pair it with the responsible executor and provide
both canonical task names. The tester sends routine production defects directly
to that executor; the executor repairs within the original capsule and returns
focused evidence; the tester reruns the failed criterion and affected
regression checks. Test, fixture, mock, or test-data defects stay with the
tester. The main agent does not relay, acknowledge, or rediagnose routine repair
traffic.

A defect packet contains the failed criterion and minimal reproduction,
observed versus expected behavior, affected file or contract, focused evidence,
and whether scope or architecture appears implicated.

Escalate to the main agent only when repair conflicts with the capsule, changes
a cross-package contract, invalidates a material decision, requires expanded
ownership, introduces security or migration risk, or the same criterion still
fails after two focused repair attempts. Escalations report the new knowledge
and exact decision needed, not the repair transcript.

## Companion Batches and Evidence

For a coherent worker group, register one Companion batch and include its
canonical task name in each dispatch envelope. Workers send detailed terminal
reports directly to Companion and only compact receipts to the main agent.
Track each lane as `expected`, `completed`, `delivered`,
`fallback-delivered`, then `reconciled`; terminal status is not delivery. If
direct delivery fails, pass the missing report and artifact references once and
mark it `fallback-only`; do not ask the worker to reproduce it. Retain all such
reports locally, then include them together in the single final reconciliation
request and mark them `fallback-delivered`. Never resend a delivered report or
call Companion once per completion. If no material conflict or synthesis remains,
the main agent may skip Companion reconciliation and decide from the compact
terminal packages.

Companion initialization ends after the batch is registered. It then remains
idle: do not ask it to wait on workers, check status, acknowledge reports, or
reconcile partial delivery. After every required report is `delivered` or
`fallback-delivered`, make exactly one reconciliation request for the batch.

Workers keep full logs, large diffs, reports, responses, screenshots,
diagnostics, and source inventories in referenced artifacts or retained thread
context. Upward evidence is concise:

```text
Claim | Result | Exact command or method | Artifact location
Critical excerpt only when needed | Confidence
```

A terminal package contains:

```text
Status | Outcome | Contract changes | New facts
Invalidated assumptions | Verification evidence | Residual risks
Decision required | Exact references
```

Use `Decision required: none` explicitly. The main agent accepts routine
operational proof without reopening artifacts unless later changes, conflict,
material uncertainty, or integration risk invalidate it.

## Failure and Takeover

- After dispatch, use the longest supported event-driven wait, preferably the
  platform maximum. User input and lifecycle events can interrupt that wait.
  Do not choose recurring one-minute or other short timeouts, call status-list
  tools for reassurance, probe workers/processes/the filesystem for activity,
  or emit "still running" updates. A timeout without new state is not progress;
  resume the long event wait without commentary, re-analysis, or Companion
  contact. A slow or quiet worker is not stall evidence.
- On each lifecycle wake, process all newly available reports in one coordinator
  turn, make only necessary dispatch or reconciliation decisions, then resume the
  long wait. Never spend a call only acknowledging delivery or regenerating an
  unchanged report.
- Reuse the responsible worker for task-local follow-up and repair.
- After one evidence-free response, send one focused evidence-oriented retry.
  If it still fails, replace it with a fresh worker carrying the capsule state
  and evidence.
- When a package is too broad or context-heavy, decompose its independent
  ownership surfaces among `default_executor` workers. Do not promote the
  monolith to `senior_executor`.
- When the remaining blocker is intrinsically difficult reasoning, send only
  the smallest hard slice to `senior_executor` before main-agent source
  takeover. Duration, breadth, or ordinary executor capacity alone is not a
  senior-executor criterion.
- Only if the appropriate replacement also fails may the coordinator take over
  the smallest critical remaining step transparently. If takeover expands into
  another source area or more than a narrow edit/check cycle, stop and
  re-delegate.
- Never weaken validation, claim unrun checks passed, accept unrelated scope,
  or allow silent error suppression or unplanned public API/schema breaks.

## Plans, Session Memory, and Completion

Session-memory documentation is off by default. Create or maintain running-
memory files only when the user explicitly enables memory for the chat or
project. Route selection, planning, implementation, or completion does not
enable it. Package-local product and technical documentation remains part of
the responsible executor's implementation when behavior would otherwise be
documented incorrectly. Use a doc-writer only for the independent scope defined
above.

For multi-package or platform/version work, before commit or closure the
behavior/integration owner or tester returns a final reconciliation with
`Requirement | Evidence | Missing proof | Final decision`. It explicitly
identifies partial modularization, uncompiled native code, untested environments,
and every other acceptance gap. After required workers finish, the main agent
summarizes the outcome, verification, limitations, and remaining work directly.
Do not create a
closure worker, documentation-only completion gate, or worker-statistics task.
When memory is enabled, update only its agreed scope. Worker statistics are
supplied only when the user requests them; do not reconstruct an exhaustive
ledger merely for statistics.
