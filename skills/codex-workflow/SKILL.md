---
name: codex-workflow
description: Explicitly invoked adaptive coding coordination for fast direct work, Luna implementation, parallel packages, difficult slices, and proportionate verification. Use when the user invokes $codex-workflow or asks to maintain codex_workflow itself.
metadata:
  short-description: Fast adaptive coding coordination
---

<!-- codex-workflow-skill-owner: codex_workflow -->

# Codex Workflow

Use one adaptive workflow for the user's coherent outcome. There are no Light,
Medium, or Heavy modes. The user's instructions take precedence over this
skill. Keep project instructions, authorization boundaries, and unrelated user
work intact.

Once explicitly invoked, keep this skill active for follow-ups on the same
outcome until completion. Do not make the user invoke it again after every
message.

## Coordinator objective

The selected main model is the coordinator. Spend its intelligence on intent,
decomposition, architecture, material uncertainty, integration decisions, and
the final answer. Minimize coordinator model and tool turns. Do not recreate
worker discovery, relay routine repair traffic, or read large raw logs and diffs
when a compact evidence report is sufficient.

Optimize total elapsed time and total work, not delegation for its own sake. A
direct five-line fix can be faster and cheaper than starting a worker that
rediscovers the module. A substantial package is usually better owned by a Luna
worker so the coordinator retains context.

For a delegated package, keep the coordinator lifecycle minimal: make one
routing decision, dispatch once, wait for events, make at most one grouped
repair decision, and finish. Additional coordinator turns require a user scope
change, blocking worker question, failed criterion, or new material evidence.
Never use a message, follow-up task, or status check merely to ask whether a
worker is still running.

If subagents are unavailable, continue directly when safe. Ask for a different
session model only when the user's requested outcome specifically requires
multi-agent execution that the current session cannot provide.

## Choose the smallest useful execution shape

### Direct

Direct workspace implementation is allowed only when the exact seam is already
known, the change introduces no new behavioral contract or nontrivial stateful
workflow, and it is expected to require one coherent patch plus at most one
cheap, proportionate verification step. Otherwise, use one Luna High Fast
`default_executor`.

If a direct change reveals unexpected complexity, stop before implementing the
larger solution and hand it to `default_executor`.

This direct path includes obvious reversible micro follow-ups when the
coordinator already knows the exact seam. Do not wake a completed worker for a
change that satisfies the direct gate.

### Delegate

Use one `default_executor` for a coherent implementation whose local discovery,
editing, and focused checks would consume meaningful coordinator context. Luna
High Fast is the normal production lane. Give it the outcome, ownership,
starting references, constraints, acceptance criteria, non-goals, and the
smallest appropriate verification boundary. Do not prescribe every file,
helper, or command.

Spawn named workflow roles with `fork_turns: "none"` and a compact task capsule.
Use a small positive turn slice only when recent conversation is uniquely
necessary. Never use an omitted or `"all"` history fork: it copies bloated
context and can inherit the expensive coordinator model instead of the role's
Luna configuration. Do not override the role's model or reasoning defaults.

### Parallelize

Use multiple `default_executor` workers only for independent mutable ownership
surfaces. Use an `investigator` only when a named material uncertainty blocks a
safe implementation decision and cannot be resolved through the executor's own
targeted discovery. Never pair an investigator and executor to inspect the same
execution path. Parallelize work that shortens the critical path; do not create
overlapping workers or redundant confirmation lanes.

For multiple workers or a task expected to require several implementation and
verification waves, read [coordination.md](references/coordination.md) before
dispatch. Otherwise do not load it.

### Difficult slice

Use at most one `senior_executor` for the smallest bounded mathematical,
logical, integration, or cross-cutting slice that genuinely needs Luna xhigh
Fast. Large files, native code, duration, breadth, or a large context window do
not qualify by themselves. The senior executor never becomes another
coordinator and does not spawn subagents.

### Diagnose or review

Read-only diagnosis, discovery, and review run zero tests, lint, formatting,
typecheck, builds, or environment checks by default. A command is allowed only
when its result is necessary to distinguish live hypotheses that source
inspection cannot answer. Name the unresolved claim before running it; never
run a check merely for confidence or because a nearby test exists.

Existing unit tests are regression gates, not diagnostic probes. Do not run
them to discover the cause of a problem. When source is inconclusive, use the
cheapest targeted observation, log, or reproduction that distinguishes the
live hypotheses. Do not announce skipped checks or narrate a no-test decision.

Use one `investigator` when a named material uncertainty must be resolved before
a safe fix, a targeted coordinator read is insufficient, and no executor can
resolve it within its own targeted discovery. Do not create an investigator to
independently confirm an executor's diagnosis. Use one `auditor`
for an explicitly requested independent review or a stable implementation with
material correctness, security, persistence, migration, release, or integration
risk. Add a `tester` only when executable independent verification has clear
value under the verification rules; low-risk work does not get a tester.

### Research external evidence (rare)

Use at most one `researcher`. Spawn it when the user explicitly requests a
dedicated research agent or research subagent.

Without that explicit request, use it only when every condition below is true:

- a named external uncertainty blocks a material architecture, feasibility, or
  debugging decision;
- the research is a standalone package with at least three independent
  questions to resolve;
- answering those questions requires reconciling at least three distinct
  primary-source families, such as separate vendor documentation, standards,
  versioned platform contracts, or authoritative source repositories;
- the package requires sustained browsing and synthesis with a plan for at
  least eight substantive source retrievals; search-result pages and repeated
  opens of the same source do not count; and
- current repository evidence or one `investigator` cannot answer it.

A single API signature, SDK option, error message, documentation page, release
note, or ordinary compatibility check never qualifies automatically. The
coordinator or current executor performs those targeted lookups directly. Give
the researcher one precise decision question, the required source boundaries,
and the expected synthesis. It is read-only and returns one compact evidence
brief; it does not implement the result.

## Preserve continuity

Reuse the current worker whenever a follow-up remains in the same module,
invariant, or ownership surface. Send only the changed requirement, new
evidence, failed criterion, and next action. Do not make a fresh worker reread
the repository, skills, documentation, and source merely because the user sent
another message.

The direct micro-follow-up rule is the exception: reuse worker context only when
the follow-up still needs local discovery, nontrivial implementation, or repair
of that worker's failed criterion.

Use a fresh worker when the task is genuinely different, independence is the
point, previous context became misleading, ownership conflicts, or the prior
worker failed to produce usable evidence after one focused retry.

## Keep discovery and verification proportional

For trivial visual, copy, documentation, or mechanical work, inspect the exact
diff. Run no command when source and diff inspection are decisive; otherwise
use at most one exact-file syntax or formatting check when relevant. Do not add
tests, run broad suites, or start a tester.

For local behavior, prefer source/diff inspection and one cheap static or
manual proof. Add a regression test only when a stable seam protects a critical
contract or a reproduced important regression. Broaden only for a changed
shared contract, meaningful cross-package risk, a failure, unresolved
uncertainty, or an explicit user request. Run a justified broad suite once at
the end, not after every repair. Never repeat a passing check without new
evidence that could invalidate it.

The implementation owner verifies once. A coordinator or reviewer trusts a
clear passing report and does not rerun it. A commit does not trigger another
check unless the commit changed files after the last proof. Broad suites
require a named cross-cutting critical risk.

Read [verification.md](references/verification.md) only when the change affects
meaningful behavior, persistence, security, native or release boundaries,
public interfaces, or needs an independent tester.

## Communication and waits

Briefly announce meaningful worker dispatches. After dispatch, use the longest
event-driven wait available. Do not poll for reassurance, emit unchanged status
updates, or wake the coordinator merely to acknowledge a report. Process all
available reports together, make the smallest next decision, and resume work.

Workers do not send routine progress messages to the coordinator while
progressing. They contact it only for a blocking decision that changes scope or
authority, then return one terminal report. Do not relay worker progress
between agents. Use `send_message` only for new user requirements or material
evidence, and `followup_task` only for a defined next unit of work on an idle
worker.

Workers return compact evidence and retain large logs locally. Accept routine
proof without replaying it unless reports conflict or a material decision needs
the decisive source.

## Authority and completion

Do not grant workers Git mutation, external mutation, destructive operations,
or broader file ownership unless the user authorized it. Existing changes are
user-owned. Session-memory documentation remains off unless the user explicitly
enables it.

Finish when the requested outcome is complete and proportionate evidence
passes. Report checks actually run, material limitations, and any required
build or manual validation. Do not add a closure worker, documentation ceremony,
or worker-statistics task.

End this workflow activation when the coherent outcome is complete. A later
unrelated request is a new outcome, not a reason to revive old workers or carry
their routing state. If the current thread is already materially large or has
compacted, recommend a fresh chat once because retained conversation context
continues to add latency and usage; continue in place if the user prefers.

For installing, updating, removing, enabling, disabling, personalizing, or
releasing codex_workflow itself, read
[maintenance.md](references/maintenance.md) and follow that lifecycle contract.
