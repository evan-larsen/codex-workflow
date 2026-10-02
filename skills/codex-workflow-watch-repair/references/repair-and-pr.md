# Repair branch and verification

Default the PR base to dev within the trusted repository allowlist. A permitted
feature branch may be selected only with concrete current-work evidence: an
active linked repair PR, explicit trusted task context, or a known matching
in-progress fix. Inspect linked PR/base/head and incident scope before starting.
Branch recency, name similarity or an arbitrary newest branch is insufficient.
Reconcile an existing repair PR instead of duplicating it. A human-edited or
unrelated branch is not exclusive worker ownership.

Record repository remote, selected base and base SHA in the proposed plan. Use an
isolated checkout/worktree and a separate incident repair branch in the configured
namespace; preserve dirty workspaces. Do not commit unrelated edits, push the
base, force-push, merge or deploy. If feature candidates conflict or the linked
PR contradicts dev, report the branch blocker; otherwise fall back to allowed dev.
Use an existing repair head only when its ownership and the incident match.

Onyx's decision must match the current correlation and plan. Before implementation,
check whether base or relevant evidence changed materially; update the plan and
Onyx decision when it invalidates the proposed approach. A missing or delayed
Onyx decision leaves the incident pending, not approved by elapsed time.

Prove the symptom/cause and affected contract locally. Use repository-supported
scoped checks; add regression protection for critical contracts. For security,
persistence, migrations or meaningful shared behavior, use focused proof plus
justified broader checks and independent review where useful. An inconclusive
confirmation or unavailable local dependency stays explicit; do not claim a
passing check or PR readiness without the required evidence.

For a shared fixed-port Docker/Supabase harness, obtain its configured exclusive
job/VM ownership before start or reset. Never reset another repair's database or
stop unrelated containers. Serialize jobs or use a repository-supported isolated
configuration; do not guess different ports to bypass the harness contract.

Before push/PR, inspect the task-owned diff, confirm only the authorized repair
branch is targeted, and reconcile any existing PR for the incident. Describe the
concrete failure, fix, base, exact local checks and missing proof. Attach the PR
when the host supports attachment. Report fingerprint, plan decision, repair
branch/PR, verification, recurrence and limitations through the configured Onyx
channel. A refused/failed transport or Git operation is reported accurately;
retry only after evidence changes or a transient failure warrants a bounded retry.
Stop when the in-scope PR/report is complete or a material blocker prevents it.
