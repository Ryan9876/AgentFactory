import unittest
from pathlib import Path
from scripts.config_loader import load_yaml, validate_constraints

ROOT = Path(__file__).resolve().parents[1]

class V2PolicyTests(unittest.TestCase):
    def test_root_guidance_and_skill_layout_are_codex_first(self):
        guidance = (ROOT / "AGENTS.md").read_text().lower()
        self.assertNotIn("cat > agents.md", guidance)
        self.assertIn("config/constraints.yaml", guidance)
        self.assertTrue((ROOT / ".agents/skills/ryan-agentfactory-stack/SKILL.md").is_file())
        self.assertFalse((ROOT / ".agents/skills").is_symlink())

    def test_constraints_encode_organization_policy(self):
        config = load_yaml(ROOT / "config/constraints.yaml")
        self.assertEqual(validate_constraints(config), [])
        self.assertEqual(config["licensing"]["github_copilot_harness"], "disallowed")
        self.assertEqual(config["work_iq"]["host_composition_with_agents"], "available")
        self.assertTrue(config["deployment"]["production_requires_explicit_approval"])

    def test_methodology_preserves_requirements_and_autonomy(self):
        text = (ROOT / ".agents/skills/ryan-agentfactory-stack/SKILL.md").read_text().lower()
        for phrase in ("original objective", "never reduce scope", "runtime qualification", "independently converge", "conditional"):
            self.assertIn(phrase, text)
        main = (ROOT / ".agents/skills/agentfactory/SKILL.md").read_text()
        self.assertIn("AUTOMATE FIRST", main)
        plan = (ROOT / "docs/superpowers/plans/2026-10-21-agentfactory-v2-final.md").read_text()
        self.assertIn("First-party tooling correction", plan)
        self.assertIn("hand off only irreducibly human steps", plan)

if __name__ == "__main__": unittest.main()
