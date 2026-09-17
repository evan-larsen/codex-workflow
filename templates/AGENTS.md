<!-- codex-workflow-id: codex_workflow -->
<!-- codex-workflow-managed-start -->
# AGENTS.md

## Project Context


## Design Principles

- Keep modules cohesive, interfaces explicit, coupling minimal, and behavior
  testable, replaceable, and reusable.
- Define proportionate acceptance and verification before implementation. Keep
  related tests cohesive; never weaken coverage, assertions, or failure
  visibility to save time or tokens.
- Preserve unrelated user work and use verified facts in durable documentation.

Project personalization and project-local instructions are in protected regions
at the end of this file. They may add project and domain constraints, but they
must defer route selection and orchestration mechanics to the selected route,
including Light's no-subagent rule. They otherwise override conflicting
workflow defaults, but not higher-level instructions.

## Working State

- `deployment state`: planning or executing a broad, possibly multi-session
  deployment plan.
- `leaf state`: work outside that plan, including general questions and small,
  bounded edits or operations.

## Project Documentation

Session-memory documentation is off by default in every route. Create or
maintain running-memory files only when the user explicitly enables memory for
the chat or project. Selecting a route, asking for a plan, installing the
workflow, completing work, or finding existing memory files does not enable
memory. Honor the stated scope; chat opt-in does not become permanent project
opt-in.

When enabled, update only relevant verified facts, decisions, progress,
blockers, and next steps in a small number of agreed files. Do not scan,
scaffold, recover, or reconcile an entire documentation framework. Preserve
existing memory files while memory is off. No route requires a closure worker
or documentation-only completion gate.

This policy does not excuse stale product or technical documentation. Update a
README, API contract, or usage guide when the requested change would otherwise
make it inaccurate. A request to edit a specific document authorizes that edit,
not ongoing session memory.

## Route Selection

There are three routes:

- **Light**: leaf-state work. The main agent works directly; no subagents.
  Project skills and local instructions cannot allocate workers in Light.
- **Medium**: deployment-state work performed by the main agent, with no
  delegated production executor or tester. Companion provides workflow-mode
  secretary and context support when useful; an explicitly requested read-only
  evidence wave never owns implementation, verification, or root-cause
  decisions. Read `~/.codex/codex_workflow/medium_route.md`.
- **Heavy**: delegation-first deployment work. The main agent coordinates and
  decides while specialized workers own operational discovery, implementation,
  focused tests, validation, and routine repair. Read
  `~/.codex/codex_workflow/heavy_route.md`.

Heavy requires the session's currently selected main agent to be
`gpt-6-astra`, `gpt-5.6-sol`, or `gpt-5.6-terra` with subagent support
available. This is a session-model requirement, not a persistent workflow
setting. If the selected model is ineligible or its subagent support is
unavailable, do not initialize a worker; ask the user to switch the current
session to Astra, Sol, or Terra. Never pin or rewrite the main model in
`config.toml`.

The user selects the route for the session. If unspecified, use Light; do not
infer Medium or Heavy. When an initial request clearly requires broad,
deployment-state work and no route was selected, give one concise recommendation
between Medium and Heavy and ask the user to choose before substantive repository
work. Do not auto-select a route. Do not interrupt work already underway merely
because it runs for a long time, uses many calls, or compacts. Light implies
`leaf state`. Medium is main-agent-led. Heavy is worker-led, including for small
workspace changes. Keep the selected route until the user changes it or the
session ends.

The selected `codex_workflow` route is the sole authority for package sizing,
worker allocation, retries and replacement, tester routing, Companion
reconciliation, coordinator takeover, and closure sequencing. Project skills
and local instructions may supply domain facts, safety limits, and repository
conventions, but MUST NOT establish a competing orchestration policy for those
mechanics.

## Context Loading

- In Light, inspect only material needed for the current task and do not create
  or use subagents, even when an applicable skill otherwise supports delegation.
- Questions and bounded tasks in Light or Medium may use the direct main-agent
  fast path. In Heavy, direct work is limited to conversation, routing, and
  one-shot read-only metadata checks. Any workspace mutation or nontrivial
  investigation is delegated, normally to one executor for a small task.
- For Medium or Heavy, read the selected route. Initialize or reuse Companion
  only when multiple workers, unfamiliar peripheral context, long-running
  context, conflicting evidence, or report-batch reconciliation makes it useful.
  Read `companion.md` before using it and `investigation_team.md` before an
  evidence wave.
- Give Companion the session goal, known constraints, escalation boundaries,
  expected task names when batching reports, and evidence format. It completes
  routine read-only work, retains operational context, and returns the director
  brief defined in its contract.
- Do not spend main-agent turns reading or re-diagnosing every routine report.
  When a worker batch exists, register one coherent batch with Companion and
  name it in the dispatch envelopes; dispatched workers deliver detailed
  terminal reports directly to it and return compact receipts to the main agent.
  Companion resolves routine matters and escalates only material knowledge or
  decisions in one director brief. If direct delivery is unavailable, hand
  Companion the compact batch once.
- The main agent reads governing instructions and directly inspects only the
  smallest decisive source or evidence needed for a material decision. In
  Heavy, workers perform broad discovery and propose the causal model; the main
  agent approves root cause, architecture, scope, and final claims without
  routinely recreating their work.
- For serious or ambiguous issues with independent search lanes, Heavy may use
  read-only investigators under `investigation_team.md`; Medium may use them
  only as explicitly requested evidence support. Investigators gather evidence;
  Companion filters their terminal report batch; the main agent opens decisive
  evidence and adjudicates the root cause.
- Resolve stale or conflicting project status with targeted evidence. Load only
  relevant module documentation and avoid replaying raw logs, large diffs,
  directory listings, or complete source files into the main context.
- Finish after proportionate verification and a concise user summary. Do not
  spawn a closure worker or reconstruct worker statistics to finish. Update
  session memory only if the user enabled it and only within the agreed scope.

## Platform Paths

Workflow documents use `/` as a platform-neutral separator. Translate paths to
the current operating system and shell when running filesystem commands.
<!-- codex-workflow-managed-end -->

<!-- codex-workflow-project-personalization-start -->
<!-- codex-workflow-project-personalization-end -->

<!-- codex-workflow-project-local-instructions-start -->
<!-- codex-workflow-project-local-instructions-end -->
