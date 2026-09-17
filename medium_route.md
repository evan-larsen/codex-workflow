# Medium Route

Use after Medium is selected under `AGENTS.md`.

The selected Medium route is the sole authority for orchestration mechanics.
Project skills may add domain and repository constraints but defer worker,
Companion, retry, and takeover behavior to this workflow.

## Role and Context

You are the main agent. Medium is the main-agent-led route: the main agent
performs planning, root-cause analysis, implementation, and verification. Do
not create production executor or tester packages in Medium.

Use Companion only when persistent context, unfamiliar peripheral discovery,
or a coherent read-only report batch materially protects main-agent attention.
Use disposable read-only investigators under `investigation_team.md` only when
the user explicitly requests an evidence wave. Even then, the support does not
transfer root-cause, implementation, or verification authority.

The main agent directly understands source it edits, decisive evidence,
material acceptance decisions, and final claims. It may use Companion to solve
routine factual questions, map peripheral context, summarize logs or artifacts,
and retain long-running operational detail.

Questions and bounded tasks may use the direct main-agent fast path without
Companion or investigators. This path does not become a deployment merely
because Medium remains selected.

## Execution

- Work in bounded context, inspection, implementation, verification, and review
  stages.
- When the user explicitly requested an evidence wave, finish it and make the
  main-agent root-cause decision before changing production behavior.
- Batch independent, already-known reads, searches, metadata checks, and
  isolated validation. Keep dependent or overlapping edits sequential.
- Run checks concurrently only when they share no mutable build output,
  generated files, fixtures, databases, ports, devices, or processes.
- Keep detailed logs in artifacts and retain only the claim, result, exact
  command or method, artifact path, critical excerpt if needed, and confidence.
- Reinspect after a change, failure, contradiction, or newly discovered
  dependency, not as routine repetition.
- Preserve unrelated work, verify in proportion to risk, and never claim an
  unrun check passed.

## Plans and Session Memory

Session-memory documentation is off by default. Create or maintain running-
memory files only when the user explicitly enables memory for the chat or
project. Selecting Medium, asking for a plan, or completing work does not enable
memory.

When memory is enabled, update only relevant verified facts, decisions,
progress, blockers, and next steps in the agreed files. Necessary product or
technical documentation remains part of the implementation when behavior would
otherwise be documented inaccurately.

## Completion

Finish when the requested outcome and proportionate verification are complete.
Summarize the result, verification, and material limitations directly. Do not
spawn a Closure Steward, reserve a worker slot, or wait for administrative
work. If memory is enabled, make only the agreed update. No automatic worker-
usage table is required.
