# Heavy coordination reference

This reference defines the execution protocol for one explicit Heavy outcome.
Its purpose is to keep an expensive parent coordinator out of routine worker
traffic while preserving strong decomposition and integration.

## Execution capsule

The parent sends the Heavy coordinator one compact capsule:

- outcome and acceptance criteria;
- current facts and only the starting files or commands already known;
- architectural decisions that are fixed versus decisions it may make;
- mutable ownership surfaces and protected or unrelated work;
- external, destructive, Git, device, and user-decision authority;
- named critical risks and the cheapest sufficient evidence;
- expected terminal report.

Do not paste the whole conversation. Use `fork_turns: "none"`. If a detail is
important enough to affect execution, state it explicitly in the capsule.

## Normal lifecycle

```text
one cohesive package:
parent -> one Luna 6 High Fast executor -> one long wait -> one batched review

true multi-package program:
parent -> one Luna 6 xhigh Fast Heavy coordinator -> one long event wait
                         |
                         +-> independent Luna 6 High Fast executors
                         +-> rare blocking investigator or hard-slice senior
                         +-> optional risk-selected audit/test after integration

Heavy coordinator: collect reports -> integrate -> one grouped repair -> report
parent: decide blocker -> one batched review -> authorized Git -> answer
```

Do not put a Heavy coordinator between the parent and a single cohesive
executor. For a real program, the parent does not supervise child workers.
Children report to the Heavy coordinator, and the Heavy coordinator reports
upward only for a decision or a terminal phase result.

## Non-polling wait protocol

`wait_agent` is event-driven and returns early. Use that property:

1. After dispatch, wait once for at least 600000 ms; prefer 3600000 ms.
2. Do not interleave status commentary, `list_agents`, reassurance messages, or
   60000 ms waits.
3. If the wait times out and nothing changed, immediately make another long
   wait. A timeout is not evidence and deserves no analysis turn.
4. When reports arrive, process all currently available reports together.
5. Resume a long wait only if useful work is still running and no decision is
   needed.

Repeated short waits multiply parent inference over an ever-growing cached
conversation while producing no implementation value. They are prohibited
even when the task is expected to take hours. Long-running work is exactly when
the longest wait should be used.

## Worker packages

Each package states one outcome, exclusive file or subsystem ownership,
constraints, acceptance criteria, non-goals, and a verification boundary. The
worker owns targeted discovery, cohesive implementation, one diff review, and
the specified proof. It returns changed surfaces, decisions, proof, and risks.

Collaboration calls are direct runtime tools and may not appear in `ALL_TOOLS`
or a nested execution-tool inventory. Their absence there does not mean they
are unavailable. A Heavy coordinator must not absorb implementation merely
because a nested-tool search does not list delegation tools.

Do not assign both an investigator and executor to rediscover the same path.
Do not split one cohesive patch merely to create parallel activity. Do not ask
workers to format, commit, summarize another worker, maintain session memory,
or provide periodic progress.

## Review and repair

Audit only a stable integrated surface and only when the risk gate or user asks
for it. One auditor returns a single prioritized packet with locations,
contract impact, and the smallest repair direction. The Heavy coordinator
routes that packet once to the correct owners, waits once, and integrates once.

A worker gets one focused repair while its context remains useful. A second
distinct failure, new phase, or changed causal model gets a fresh worker with a
compact evidence capsule instead of extending a bloated thread.

After the terminal report, the parent uses one batched status/diff inspection
by default. It reads individual changed files only when the report, diff, or a
named critical risk identifies a concrete concern. All actionable findings go
back as one repair packet rather than one follow-up per observation.

## Verification and human boundaries

Verification protects named critical contracts; it does not prove every file
was touched correctly. Trust a clear passing worker report and do not rerun it.
Batch any justified broad check once after the integrated phase is stable.

Each package gets one planned terminal proof batch: the smallest focused
regression proof required by the named risk and at most one relevant static
check. Do not run lint merely because TypeScript changed, and do not alternate
tests, typecheck, lint, and patching to accumulate confidence. If proof finds a
defect, repair it and rerun only the failed or directly affected proof. A
presentation, documentation, accessibility-label, or similarly low-risk
follow-up does not invalidate already passing behavioral tests or typecheck.

When only a device, provider, or human can resolve the remaining uncertainty,
return one consolidated request to the parent and let workers end. After the
observation arrives, start or resume only the worker that owns the affected
boundary.
