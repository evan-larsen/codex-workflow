# User-runtime and legacy project migration

Version 2.2.0 updates older user-level installations to the Sol, Luna and watch
repair skills and their fixed role templates. Bootstrap/update preserve every
project file; --project and --legacy-local-instructions are retained compatibility
inputs and do not rewrite project AGENTS.md or initialize session memory.

Obtain the v2.2.0 archive and SHA256SUMS, verify the checksum, extract the package
and run its workflow.py validate before installation. For an older runtime, run
the incoming workflow.py update --source <extracted-package> --codex-home <home>.
The CLI rejects equal versions and requires --allow-downgrade for a downgrade.
Updates back up the installed runtime, replace marked owned skills/roles, retire
marked legacy skills/roles and preserve unrelated settings and unmarked content.
An unmarked incoming skill/role collision blocks mutation; do not delete it to
force an installation.

Legacy v1 project wrappers and their repository-qualified markers remain
recognized by the explicit remove lifecycle so captured local instructions can
be restored. Removal has a read-only plan and separate confirmed phase; inspect
the plan before authorizing it. It preserves project memory documents and
unrelated instructions. No automatic project migration is performed on update.
