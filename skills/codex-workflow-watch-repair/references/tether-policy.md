# Tether policy example

Apply this reference only to a trusted Tether incident. Resolve repository paths,
remote, permitted bases and the existing Tether Ops Google Sheet identity/range
from trusted configuration; do not infer them from the email. Default base is dev.
Feature bases need the current-work and PR evidence in repair-and-pr.md.

The existing Tether Ops Google Sheet is the fingerprint/deduplication/recurrence
ledger. Read its current structure before a precise authorized update; preserve
its columns and other incidents. Repeated delivery during a pending Onyx decision
updates the incident evidence rather than creating a second repair. Ledger writes
are incident tracking under standing delegation, not permission for application
hosted writes. Use the available Google Drive/Sheets skill for connected sheet work.

Give the read-only Luna High investigator a bounded Supabase/PostHog confirmation
question. Load the applicable Supabase and PostHog skills when using those tools;
collect only decisive evidence. Do not change production rows, RLS, schema,
functions, flags or analytics configuration. If a plugin is unavailable or evidence
is stale/ambiguous, return inconclusive with the missing proof.

For database contracts, use the repository's existing loopback Docker/local
Supabase ABI harness: reset:supabase-contract:local followed by
verify:supabase-contract:local through the repository-supported runner. The local
Postgres port is 54322. Confirm the harness targets the permitted disposable local
instance and obtain exclusive harness ownership before resetting. Active
migrations are the schema authority; do not repair against archived migrations
or a guessed hosted schema. No linked-project reset or hosted migrations.

Keep plan ready, implementing, local verification passed, PR ready/awaiting human
merge, and production resolved distinct using the Sheet's existing conventions.
Only later post-merge runtime evidence supports production resolved. This example
requires no Tether plugins, Sheet, or Supabase harness for unrelated repositories.
