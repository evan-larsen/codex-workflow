---
name: codex-workflow-heavy
description: Explicitly invoked long-horizon coding coordination for multi-phase or multi-surface work using one Luna xhigh Fast execution coordinator and bounded Luna workers. Use only when the user invokes $codex-workflow-heavy.
metadata:
  short-description: Efficient long-horizon coding coordination
---

<!-- codex-workflow-heavy-skill-owner: codex_workflow -->

# Codex Workflow Heavy

Use this skill only when the user explicitly invokes `$codex-workflow-heavy`.
It is the long-horizon companion to `$codex-workflow`, not a mode inside that
skill. Keep it active for follow-ups on the same coherent outcome until that
outcome is complete.

Read [heavy-coordination.md](references/heavy-coordination.md) before the first
dispatch. The user's instructions, project rules, authorization boundaries,
and unrelated work remain authoritative.

## When Heavy is useful

Heavy is designed for an implementation program with multiple phases,
independent ownership surfaces, cross-layer integration, or enough sustained
execution that the selected parent model should preserve its context for
decisions. Duration, a large file, or the user's desire for one small subagent
does not by itself require a large worker topology. An explicitly invoked but
indivisible task may still use one executor.

Do not recreate the retired ceremony: no automatic memory documents, companion
agent, closure worker, default tester, documentation gate, worker statistics,
or repeated status narration.

## Parent coordinator contract

The selected main model owns only user intent, architectural constraints,
material decisions, authorization, final integration judgment, and the final
answer. It should use as few tokens and tool turns as possible.

1. Build one compact execution capsule containing the outcome, known starting
   points, ownership boundaries, protected areas, acceptance criteria,
   authority limits, and risk-selected verification boundary.
2. Spawn exactly one `heavy_coordinator` with `fork_turns: "none"`. Do not
   override its packaged Luna xhigh Fast configuration.
3. Let that coordinator own worker decomposition, implementation traffic,
   integration, and one grouped repair wave. Do not separately supervise or
   poll its children.
4. Wake for a real blocker, a user scope change, a requested external or
   destructive action, or the terminal phase report. Handle a tiny final Git or
   metadata integration action directly when authorized; never wake a worker
   solely to format, stage, commit, inspect status, or report that it committed.
5. Finish from the compact report and decisive diff evidence. Do not replay
   large logs or rerun clear passing proof.

## Waiting is one event-driven operation

After dispatch, call `wait_agent` with `timeout_ms` of at least 600000. Prefer
the maximum supported value, currently 3600000, because the wait returns early
as soon as an agent completes, reports a blocker, or the user steers the task.

Never use recurring 60000 ms waits, minute-by-minute polling, or a commentary
message whose only purpose is to say that an agent is still working. A timeout
with no report is not a new coordination event: immediately begin another long
wait without commentary or other model work. Do not call `list_agents` merely
for reassurance. Multi-turn waiting is a workflow failure, not progress.

Process accumulated reports in one batch. Send a message only when new user
input or material evidence changes the assigned work. Send a follow-up only for
a concrete next unit or one grouped repair packet after a terminal report.

## Execution topology

The Heavy coordinator normally uses Luna High Fast `default_executor` workers
for disjoint implementation packages. It may use one Luna xhigh Fast
`senior_executor` for an intrinsically difficult bounded slice. An
`investigator` is allowed only for a named uncertainty that blocks a safe
decision and cannot be resolved inside an executor's targeted discovery.

Independent audit and testing are risk-selected, not phase rituals. Use an
`auditor` only for material correctness, security, persistence, migration,
release, or integration risk, or when the user explicitly requests independent
review. Use a `tester` only when executable independent proof has clear value
for such a critical contract. Ordinary UI, tooling, documentation, mechanical
refactors, and low-risk bug fixes do not get automatic test or review lanes.

A rare `researcher` is allowed only under the strict external-research gate in
the normal workflow or when the user explicitly requests dedicated research.
Do not create research workers for ordinary documentation or API lookups.

## Phase and repair discipline

Give every worker exclusive mutable ownership and a terminal deliverable. Run
independent packages in parallel; keep dependent packages sequential. Prefer a
small number of meaningful packages over many tiny handoffs.

Collect implementation results before review. Give the auditor one stable
integrated surface, then return all actionable findings as one prioritized
repair packet. Do not alternate audit and repair one finding at a time. Reuse a
worker for its original package and one focused repair; use a fresh compact
capsule after a phase change, materially different causal hypothesis, or
second distinct failure.

For device-, provider-, or human-judgment boundaries, complete everything that
can be proven locally, then ask for one consolidated observation. Do not keep
workers alive while waiting for the user. Route the returned evidence once.

## Completion

Complete after the requested outcome is integrated and its risk-selected
evidence is sufficient. Report changes, checks actually run, limitations, and
any build or manual boundary. Do not add broad suites, formatting, lint,
typecheck, builds, documentation closure, or another reviewer merely to make
the workflow feel complete.
