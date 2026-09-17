# codex_workflow maintenance

Use this reference only for bootstrapping, updating, checking, removing,
releasing, or diagnosing codex_workflow itself.

The canonical source is the public repository
`evan-larsen/codex-workflow`. The installed runtime is
`~/.codex/codex_workflow` or the configured `CODEX_HOME`. Installed files are
release-derived copies, not canonical source.

Use the installed lifecycle guides for the requested operation:

- first bootstrap: `~/.codex/codex_workflow/bootstrap.md`
- update: `~/.codex/codex_workflow/update.md`
- check for updates: `~/.codex/codex_workflow/check_update.md`
- remove: `~/.codex/codex_workflow/remove.md`

A source edit does not authorize commit, push, release publication, installed
runtime replacement, or project migration. Obtain the authority required for
each shared or external mutation.

Do not write project `AGENTS.md`, personalization, state, or documentation
during bootstrap or update. Preserve unrelated settings. Refuse to overwrite or remove an unmarked global skill.
Only a skill carrying the codex_workflow ownership marker may be replaced or
removed by lifecycle operations.

Validate the package and run focused lifecycle tests. Installation and update
changes require isolated temporary-runtime coverage for fresh install,
replacement, collision refusal, owned legacy migration, and removal as
applicable. After a global runtime change, tell the user to refresh or restart
Codex so skill discovery reloads the instructions.
