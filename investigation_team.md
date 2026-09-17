# Investigation Team

Use this shared contract for Heavy, and for a Medium evidence wave, when a
serious or ambiguous issue has a search space that can be divided into
independent read-only lanes. Investigators are disposable evidence gatherers.
Companion is the optional persistent report wrapper when multiple lanes or
conflicting evidence need reconciliation.

## Coordinator Grounding

Before dispatch, the main agent reads the governing instructions, user
requirements, acceptance boundaries, and enough exact starting context to frame
discriminating questions. It does not need to trace the complete source path,
interfaces, invariants, contracts, logs, or reproduction before delegation;
that operational discovery belongs to investigators.

The coordinator names the decision that evidence must support and any protected
scope. It later approves the causal model from concise evidence and exact
references, opening only the smallest decisive source or artifact needed for a
material judgment. Delegation transfers discovery work, not decision authority.

## Dispatch Gate

Create multiple lanes only when multiple plausible causes, cross-system
behavior, flaky or concurrent failure, security or performance risk,
dependency/version uncertainty, missing reproduction, or external prior art
makes parallel search materially useful. Use one investigator for one bounded
uncertainty. Skip investigation for a known root cause or established
implementation boundary. Do not create duplicate lanes merely to use capacity.

For each orthogonal lane, spawn one worker with `agent_type="investigator"`, a
unique `task_name="investigator_<deployment_id>_<lane>"`, and
`fork_turns="none"`. Supply the question or hypothesis, boundaries, known
facts, preferred authoritative sources, useful exact starting references,
forbidden scope, and evidence format.

Each lane must remove a named decision-relevant uncertainty that cannot be
resolved from known evidence or ordinary executor-owned package discovery. Do
not use investigators as routine implementation preflight, generic code
mapping, or a way to keep local discovery out of an executor capsule.

Useful lanes include execution paths and state, failure reproduction and logs,
tests and races, dependency or version behavior, security or performance
boundaries, official documentation and source history, and clearly labeled
technical-forum or prior-art searches.

Investigator quantity is driven by the smallest set of independent lanes with
positive information value. Cost and coordination overhead are tie-breakers;
do not continue investigation after enough evidence exists to route the next
action.

## Companion Batch

When two or more lanes, conflicting evidence, or long-running context makes
reconciliation useful, initialize or reuse Companion. Register one batch ID,
the expected investigator task names, and the escalation boundary. Include
Companion's canonical task name and the batch ID in each lane brief.

Investigators deliver detailed terminal evidence directly to Companion and
return only a compact receipt to the main agent with
`delivery_state=delivered` or `delivery_state=fallback_required`. Mark terminal
workers `completed`, but wait for `delivered` or one controlled fallback before
asking Companion to reconcile. If direct delivery fails, the main agent passes
each missing report and artifact references once and marks it
`fallback-delivered`. Never resend a delivered report.

For one investigator without Companion, return the concise evidence package
directly to the main agent.

## Evidence and Root-Cause Approval

An investigator reports the hypothesis, evidence for and against,
reproduction or falsification method, exact local references, external sources
and authority level, competing explanation, confidence, and recommended next
experiment. It proposes but does not declare the authoritative root cause or
implementation plan.

When Companion is used, it deduplicates evidence, reconciles routine
discrepancies, identifies conflicts and missing proof, resolves bounded factual
questions, and returns one director brief. It does not manage investigators.

The main agent reviews the brief or direct evidence package, compares only
material competing hypotheses, and records whether the cause is confirmed,
probable, or unresolved. Do not package a production fix until it can state the
affected contract, fix boundary, residual uncertainty, and acceptance test.
This is an approval gate, not a requirement to repeat the investigators' work.

If the gate is not met, reuse the relevant investigator thread with one compact
evidence delta or run one diagnostic experiment. Do not launch another broad
wave by default. After the gate, Medium keeps implementation and verification
in the main agent; Heavy delegates implementation to an executor and adds a
tester only when the Heavy verification risk gate is satisfied.
