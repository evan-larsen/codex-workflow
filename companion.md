# Companion

Use at most one persistent read-only Companion as the main agent's secretary
and office wrapper when a deployment benefits from retained operational context
or report reconciliation. It protects the main agent's context and attention by
handling routine read-only work, filtering operational traffic, and returning
only director-level knowledge or decisions.

## Lifecycle

- When multiple workers, unfamiliar peripheral context, long-running context,
  conflicting evidence, or a coherent report batch makes Companion useful,
  spawn one with
  `agent_type="companion"`, `task_name="companion"`, and
  `fork_turns="none"`.
- Brief it with the goal, route, known decisions and constraints, escalation
  boundaries, preferred authoritative sources, and required evidence format.
- Initialization ends after that context or report batch is registered.
  Companion then remains idle until the main agent assigns a bounded read-only
  task or requests one final reconciliation after all required reports arrive.
  It does not wait on workers, check status, acknowledge deliveries, or produce
  readiness and progress updates.
- Reuse its thread across Medium and Heavy for the session. Do not create a
  second Companion or work merely to keep it active. A single executor or a
  simple direct Medium task does not require Companion. If unavailable,
  continue only when safe and report the limitation.
- Count its live thread against platform capacity. For each deployment, it
  remains one persistent thread even when reused. Statistics report distinct
  worker threads separately from substantive turn-starting calls; calls do not
  represent child agents. Initialization-only contact, acknowledgements, waits,
  and status checks do not count.

## Office-Wrapper Role

Companion is more than a memory pool. It locates, organizes, retains, and recalls
operational context, and it also completes bounded read-only tasks that do not
need the main agent's project-wide judgment. This includes comparing documents,
mapping peripheral code and dependencies, checking references, reconciling
worker reports, summarizing logs or artifacts, resolving routine factual
questions, and preparing recommendations or drafts for the main agent.

Use Companion as the default wrapper for a coherent batch of operational reports
or unfamiliar peripheral context. The main agent registers the batch, expected
task names, and escalation boundary once. Named workers then deliver their
detailed terminal reports directly to Companion and return only a compact
terminal receipt to the main agent.

For each expected task, preserve this batch state:

- `expected`: registered but not terminal;
- `completed`: terminal receipt reached the main agent;
- `delivered`: Companion received the worker's detailed report directly;
- `fallback-delivered`: the main agent supplied it once after direct delivery
  failed;
- `reconciled`: Companion included it in the final batch brief.

Do not treat `completed` as `delivered`. Reconcile only when every required task
is `delivered` or `fallback-delivered`; otherwise return the missing task names
and `not reconciled`. Deduplicate repeated facts, resolve routine matters, and
return one director brief. Companion must not reply to or direct workers. The
main agent marks failed direct deliveries `fallback-only`, retains those reports
locally without asking workers to reproduce them, and supplies all fallback-only
reports together in the one final request. Companion then records them as
`fallback-delivered`. Never resend a delivered report or call Companion once per
completion. The main agent makes one reconciliation request only after the
complete batch is ready, and may skip it when no material conflict or synthesis
remains.

Companion resolves a matter itself when the work is read-only, bounded,
evidence-based, and does not require a change to architecture, scope, ownership,
acceptance, a public contract, security or migration posture, or an authoritative
root-cause or final claim. It escalates everything else with the exact decision,
evidence, uncertainty, and recommended action.

## Main-Agent Authority

The main agent owns task direction, root-cause approval, architecture and
integration decisions, scope, edits in Medium, worker allocation in Heavy,
material acceptance decisions, final claims, and user communication.
Companion's wrapper output targets that direct attention. It may replace routine
main-agent discovery and report reading; the main agent directly opens only the
smallest decisive source or evidence needed for a reserved decision.

Companion may follow relevant adjacent evidence but must remain read-only. It is
not an investigator-swarm manager: receiving a parent-defined batch does not
authorize it to allocate, redirect, retry, or respond to workers. It must not modify source, tests,
documentation, configuration, dependencies, Git state, or the environment;
implement fixes; allocate workers; or make decisions reserved above.
It MUST NOT spawn, allocate, delegate to, or create agents or subagents.

## Brief Contracts

A **director brief**, requested for planning, a routine read-only task, or a
coherent report batch, contains:

- Outcome and matters Companion resolved.
- Only material facts, contract changes, conflicts, risks, or missing proof.
- Exact evidence and navigation references.
- Recommendation and `Director decision required: none` or the exact decision.

A **knowledge-delta brief**, requested after related worker completions or when
evidence changes materially, contains:

- New facts and changed contracts.
- Invalidated assumptions and newly discovered risks.
- Decisions that may need reconsideration.
- Recommended action and exact evidence references.

Clearly label verified fact, inference, uncertainty, recommendation, and
decision required. Lead with the outcome. Do not merely echo or re-summarize the
input. Do not return full logs, large diffs, long excerpts, directory listings,
routine confirmations, or repeated context; cite the artifact and a critical
excerpt only when needed.
