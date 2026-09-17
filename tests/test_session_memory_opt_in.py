"""Regression checks for installation without implicit session-memory opt-in."""

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from runtime.layout import PackageLayout, ProjectPaths
from runtime.project_ops import plan_project_install


class SessionMemoryInstallationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = PackageLayout.resolve(PACKAGE_ROOT)

    def test_fresh_install_and_reinstall_do_not_create_memory_or_workers(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            for _ in range(2):
                plan = plan_project_install(self.package, project)
                self.assertEqual(plan.agent_actions, [])
                self.assertFalse(any(project.docs in m.path.parents for m in plan.mutations))
                plan.apply()
                self.assertTrue(project.active.is_file())
                self.assertTrue(project.personalization.is_file())
                self.assertFalse(project.docs.exists())

    def test_existing_and_template_marked_memory_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            project.docs.mkdir()
            original = {
                'project_progress.md': b'User-owned progress\r\n',
                'latest_session_work.md': b'<!-- codex-workflow-bootstrap-template -->\n',
            }
            for name, content in original.items():
                (project.docs / name).write_bytes(content)
            plan = plan_project_install(self.package, project)
            self.assertEqual(plan.agent_actions, [])
            plan.apply()
            self.assertEqual({p.name: p.read_bytes() for p in project.docs.iterdir()}, original)

    def test_disabled_reinstall_stays_disabled_without_memory_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            plan_project_install(self.package, project).apply()
            project.active.rename(project.disabled)
            plan = plan_project_install(self.package, project)
            self.assertEqual(plan.agent_actions, [])
            plan.apply()
            self.assertTrue(project.disabled.is_file())
            self.assertFalse(project.active.exists())
            self.assertFalse(project.docs.exists())


if __name__ == '__main__':
    unittest.main()
