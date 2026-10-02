"""Linux bootstrap execution and cross-platform shell archive contracts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.package import build


class ShellArchiveTests(unittest.TestCase):
    def test_shell_archive_is_lf_executable_and_independent_of_checkout_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            script = root / "bootstrap.sh"
            script.write_bytes(b"#!/usr/bin/env bash\r\nexit 0\r\n")
            first, _ = build(root, Path(directory) / "first")
            with zipfile.ZipFile(first) as archive:
                entry = archive.getinfo("codex_workflow/bootstrap.sh")
                self.assertEqual(entry.create_system, 3)
                self.assertEqual((entry.external_attr >> 16) & 0o777, 0o755)
                self.assertEqual(archive.read(entry), b"#!/usr/bin/env bash\nexit 0\n")
            script.write_bytes(b"#!/usr/bin/env bash\nexit 0\n")
            second, _ = build(root, Path(directory) / "second")
            self.assertEqual(first.read_bytes(), second.read_bytes())


@unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("bash") and shutil.which("unzip"), "requires Linux bash and unzip")
class LinuxBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="workflow-linux-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive, self.sums = build(ROOT, self.root / "package with spaces")
        self.extracted = self.root / "review"
        subprocess.run(["unzip", "-q", str(self.archive), "-d", str(self.extracted)], check=True)
        self.bootstrap = self.extracted / "codex_workflow/scripts/bootstrap.sh"
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("user instructions\n", encoding="utf-8")
        self.home = self.root / "codex home"
        self.home.mkdir()
        (self.home / "config.toml").write_text('model = "user-model"\n', encoding="utf-8")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.codex = self.bin / "codex"
        self.codex.write_text("#!/usr/bin/env bash\nprintf 'codex-cli 0.147.0\\n'\n", encoding="utf-8")
        self.codex.chmod(0o755)
        self.scratch = self.root / "scratch"
        self.scratch.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"], TMPDIR=str(self.scratch), CODEX_WORKFLOW_PYTHON=sys.executable)
        self.env.pop("CODEX_HOME", None)

    def run_bootstrap(self):
        return subprocess.run([str(self.bootstrap), "--archive", str(self.archive), "--checksums", str(self.sums), "--project", str(self.project), "--codex-home", str(self.home)], env=self.env, capture_output=True, text=True, check=False)

    def test_fresh_install_and_upgrade_preserve_paths_and_clean_extraction(self):
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list(self.scratch.iterdir()), [])
        self.assertEqual((self.project / "AGENTS.md").read_text(), "user instructions\n")
        self.assertFalse((self.project / "agent_docs").exists())
        self.assertIn('model = "user-model"', (self.home / "config.toml").read_text())
        state = json.loads((self.home / "codex_workflow/install_state.json").read_text())
        self.assertEqual(set(state["owned_skills"]), {"codex-workflow-sol", "codex-workflow-luna", "codex-workflow-watch-repair"})
        self.assertTrue((self.home / "agents/default_executor.toml").is_file())
        # Exercise the real incoming CLI update route against a simulated older runtime.
        runtime = self.home / "codex_workflow"
        (runtime / "VERSION").write_text("2.0.4\n", encoding="utf-8")
        state["version"] = "2.0.4"
        (runtime / "install_state.json").write_text(json.dumps(state), encoding="utf-8")
        incoming = self.extracted / "codex_workflow"
        command = [sys.executable, str(incoming / "workflow.py"), "update", "--source", str(incoming), "--project", str(self.project), "--codex-home", str(self.home), "--json"]
        updated = subprocess.run(command, env=self.env, capture_output=True, text=True)
        self.assertEqual(updated.returncode, 0, updated.stdout + updated.stderr)
        self.assertEqual((runtime / "VERSION").read_text().strip(), (ROOT / "VERSION").read_text().strip())
        rejected = subprocess.run(command, env=self.env, capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("matches the installed version", rejected.stdout + rejected.stderr)

    def test_incompatible_codex_fails_before_install_and_cleans_extraction(self):
        self.codex.write_text("#!/usr/bin/env bash\nprintf 'codex-cli 0.1.0\\n'\n", encoding="utf-8")
        result = self.run_bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / "codex_workflow").exists())
        self.assertEqual(list(self.scratch.iterdir()), [])
        self.assertEqual((self.home / "config.toml").read_text(), 'model = "user-model"\n')


if __name__ == "__main__":
    unittest.main()
