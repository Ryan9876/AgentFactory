"""Anti-regression checks for lessons learned carried into AgentFactory."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/agentfactory/SKILL.md"
GUARDRAILS = ROOT / ".agents/skills/agentfactory/references/engineering-guardrails.md"


class LessonsLearnedGuardrailTests(unittest.TestCase):
    def test_factory_skill_requires_lessons_learned_gate(self):
        skill = SKILL.read_text().lower()
        self.assertIn("lessons-learned gate", skill)
        self.assertIn("references/engineering-guardrails.md", skill)
        self.assertIn("stop the affected work", skill)
        self.assertIn("change path", skill)

    def test_guardrails_preserve_core_work_radar_lessons(self):
        text = GUARDRAILS.read_text().lower()
        required = (
            "use → configure → integrate → automate → extend → build",
            "runtime qualification",
            "failure taxonomy",
            "user_presence_required",
            "no pac push without a fresh pre-push pull",
            "explicit command exit code",
            "never invent a component guid",
            "restore_hash_known",
            "zero_write_test_path",
            "typed contract",
            "identity",
            "idempotency",
            "security contract",
            "repeatability fixtures",
            "no architecture redesign solely because one microsoft authoring surface is malfunctioning",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_guardrails_are_conditional_not_work_radar_architecture_defaults(self):
        text = GUARDRAILS.read_text().lower()
        self.assertIn("do not overfit future agents to work radar", text)
        self.assertIn("apply them only", text)
        self.assertIn("examples, not universal agentfactory requirements", text)

    def test_browser_identity_and_regression_profiles_are_separate(self):
        text = GUARDRAILS.read_text().lower()
        self.assertIn("chrome stable", text)
        self.assertIn("profile `agentfactory`", text)
        self.assertIn("chrome for testing", text)
        self.assertIn("disposable isolated profile", text)
        self.assertIn("do not use this authenticated profile for generic automation", text)


if __name__ == "__main__":
    unittest.main()
