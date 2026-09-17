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

If subagents are unavailable, continue directly when safe. Ask for a different
session model only when the user's requested outcome specifically requires
multi-agent execution that the current session cannot provide.

## Choose the smallest useful execution shape

### Direct

Work directly when the answer or edit has a known narrow seam and delegation
would cost more time or context than the work itself. This includes
conversation, metadata, targeted read-only questions, and obvious reversible
micro-edits. Use one targeted inspection batch, make the edit, and run at most
one proportionate check. Escalate only when the first evidence changes the
boundary or reveals material risk.

### Delegate

Use one `default_executor` for a coherent implementation whose local discovery,
editing, and focused checks would consume meaningful coordinator context. Luna
high Fast is the normal production lane. Give it the outcome, ownership,
starting references, constraints, acceptance criteria, non-goals, and the
smallest appropriate verification boundary. Do not prescribe every file,
helper, or command.

### Parallelize

Use multiple `default_executor` workers only for independent mutable ownership
surfaces. Use investigators only for independent uncertainties that block a
decision or can run alongside useful implementation. Parallelize work that
shortens the critical path; do not create overlapping workers or redundant
confirmation lanes.

For multiple workers or a task expected to require several implementation and
verification waves, read [coordination.md](references/coordination.md) before
dispatch. Otherwise do not load it.

### Difficult slice

Use at most one `senior_executor` for the smallest bounded mathematical,
logical, integration, or cross-cutting slice that genuinely needs Luna xhigh.
Large files, native code, duration, breadth, or a large context window do not
qualify by themselves. The senior executor never becomes another coordinator
and does not spawn subagents.

### Diagnose or review

Use one `investigator` when a material uncertainty must be resolved before a
safe fix and a targeted coordinator read is insufficient. Use one `auditor`
for an explicitly requested independent review or a stable implementation with
material correctness, security, persistence, migration, release, or integration
risk. Add a `tester` only when executable independent verification has clear
value under the verification rules.

## Preserve continuity

Reuse the current worker whenever a follow-up remains in the same module,
invariant, or ownership surface. Send only the changed requirement, new
evidence, failed criterion, and next action. Do not make a fresh worker reread
the repository, skills, documentation, and source merely because the user sent
another message.

Use a fresh worker when the task is genuinely different, independence is the
point, previous context became misleading, ownership conflicts, or the prior
worker failed to produce usable evidence after one focused retry.

## Keep discovery and verification proportional

For trivial visual, copy, documentation, or mechanical work, inspect the exact
diff and run only an exact-file syntax or formatting check when relevant. Do
not add tests or run broad suites by default.

For local behavior, run the nearest focused test or static check. Broaden only
for a changed shared contract, meaningful cross-package risk, a failure,
unresolved uncertainty, or an explicit user request. Run a justified broad
suite once at the end, not after every repair. Never repeat a passing check
without new evidence that could invalidate it.

Read [verification.md](references/verification.md) only when the change affects
meaningful behavior, persistence, security, native or release boundaries,
public interfaces, or needs an independent tester.

## Communication and waits

Briefly announce meaningful worker dispatches. After dispatch, use the longest
event-driven wait available. Do not poll for reassurance, emit unchanged status
updates, or wake the coordinator merely to acknowledge a report. Process all
available reports together, make the smallest next decision, and resume work.

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

For installing, updating, removing, enabling, disabling, personalizing, or
releasing codex_workflow itself, read
[maintenance.md](references/maintenance.md) and follow that lifecycle contract.
