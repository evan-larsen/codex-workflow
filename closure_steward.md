# Optional Scoped Memory Update

Closure Steward is retained for compatibility, not automatic deployment
closure. Session-memory documentation is off by default in every route. Create
or maintain running-memory files only when the user explicitly enables memory
for the chat or project. Route selection, planning, implementation, completion,
or finding existing memory files does not enable memory.

When memory is enabled, the main agent normally updates only the relevant
verified facts, decisions, progress, blockers, and next steps in a small number
of agreed files. Do not scan, scaffold, recover, or reconcile an entire
documentation framework. Preserve existing memory files when memory is off. No
route requires a closure agent or documentation-only completion gate.

Necessary product or technical documentation is separate from session memory.
Update a README, API contract, or usage guide when the requested change would
otherwise make it inaccurate.

Prefer a direct main-agent update in Medium. In Heavy, use this worker only for
a substantial independent memory assignment within explicit user
authorization. Give it the user's authorization, exact target files, verified
facts and evidence, and a stopping condition. Use `fork_turns="none"`; do not
require reconstruction of the conversation. Do not reserve capacity for it or
spawn it on completion, pause, or blockage by default.

If it stalls, stop it and report the unfinished memory update separately. Do
not keep completed implementation waiting through repeated status requests.
Never claim an update completed without evidence.
