import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class SkillLayoutTests(unittest.TestCase):
    def test_canonical_skills_are_real_and_discoverable(self):
        skills = ROOT / ".agents/skills"
        self.assertTrue(skills.is_dir())
        self.assertFalse(skills.is_symlink())
        for name in ("agentfactory", "ryan-agentfactory-stack", "agent-spec-verifier", "power-platform-resilience"):
            self.assertTrue((skills / name / "SKILL.md").is_file(), name)
        self.assertIn("name: agentfactory", (skills / "agentfactory/SKILL.md").read_text())
    def test_active_code_and_tests_do_not_use_old_skill_paths(self):
        for path in (ROOT / "tests").glob("*.py"):
            stale = ".github/skills/" + "m365-agent-factory"
            self.assertNotIn(stale, path.read_text(), path.name)
if __name__ == "__main__": unittest.main()
