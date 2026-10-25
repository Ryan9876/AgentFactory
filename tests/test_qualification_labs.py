"""Contract tests for the resumable four-lab qualification index."""

from pathlib import Path
import hashlib
import json
import unittest
from copy import deepcopy

from scripts.config_loader import evaluate_architecture_candidates, load_yaml


ROOT = Path(__file__).resolve().parents[1]
INDEX = load_yaml(ROOT / "config/qualification-labs.yaml")
LABS = INDEX["labs"]


class QualificationLabsTests(unittest.TestCase):
    def _lab_b_candidates(self):
        lab = LABS["B"]
        shared = lab["shared_lifecycle_requirements"]
        return [
            {
                "name": candidate["name"],
                "requires": [*shared, *candidate["requires"]],
            }
            for candidate in lab["architecture_candidates"]
        ]

    def test_lab_b_sideload_blocks_only_agents_toolkit_candidate(self):
        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        result = evaluate_architecture_candidates(
            self._lab_b_candidates(),
            registry["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["evaluations"][0]["status"], "REJECTED_CURRENT_ENVIRONMENT")
        self.assertIn(
            "agents_toolkit.custom_app_upload",
            [item["capability"] for item in result["evaluations"][0]["blockers"]],
        )
        self.assertEqual(result["evaluations"][1]["name"], "WIQD Personal owner-only")
        self.assertEqual(result["status"], "BLOCKED_UNVERIFIED_REQUIREMENT")

    def test_lab_b_candidate_prerequisites_are_registered_and_evidence_mapped(self):
        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        registered = set(registry["capabilities"])
        availability = registry["environment_constraints"]["capability_availability"]
        for candidate in self._lab_b_candidates():
            for capability in candidate["requires"]:
                with self.subTest(candidate=candidate["name"], capability=capability):
                    self.assertIn(capability, registered)
                    self.assertIn(capability, availability)

    def test_lab_b_unverified_wiqd_prerequisites_fail_closed(self):
        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        result = evaluate_architecture_candidates(
            [self._lab_b_candidates()[1]],
            registry["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "BLOCKED_UNVERIFIED_REQUIREMENT")
        self.assertEqual(result["evaluations"][0]["status"], "NOT_YET_QUALIFIED")

    def test_lab_b_viable_wiqd_candidate_selected_without_clearing_sideload(self):
        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        availability = deepcopy(registry["environment_constraints"]["capability_availability"])
        for capability in self._lab_b_candidates()[1]["requires"]:
            availability[capability] = {
                "environment_availability": "available",
                "classification": "CURRENT_ENVIRONMENT_AVAILABLE",
            }
        self.assertEqual(
            availability["agents_toolkit.custom_app_upload"]["environment_availability"],
            "unavailable",
        )
        result = evaluate_architecture_candidates(self._lab_b_candidates(), availability)
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["architecture"], "WIQD Personal owner-only")
        self.assertEqual(result["evaluations"][0]["status"], "REJECTED_CURRENT_ENVIRONMENT")

    def test_personal_candidate_does_not_require_optional_share_or_azure(self):
        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        availability = deepcopy(registry["environment_constraints"]["capability_availability"])
        personal = self._lab_b_candidates()[1]
        self.assertEqual(personal["name"], "WIQD Personal owner-only")
        for capability in personal["requires"]:
            availability[capability] = {
                "environment_availability": "available",
                "classification": "CURRENT_ENVIRONMENT_AVAILABLE",
            }
        for capability in ("wiqd.direct_user_share", "azure.subscription_access_for_provisioning"):
            self.assertNotIn(capability, personal["requires"])
            availability[capability] = {
                "environment_availability": "unavailable",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            }
        result = evaluate_architecture_candidates(self._lab_b_candidates(), availability)
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["architecture"], personal["name"])
        self.assertEqual(result["evaluations"][0]["status"], "REJECTED_CURRENT_ENVIRONMENT")
        for capability in ("wiqd.direct_user_share", "azure.subscription_access_for_provisioning"):
            self.assertEqual(availability[capability]["environment_availability"], "unavailable")

    def test_index_defines_all_original_labs_and_persisted_evidence(self):
        self.assertEqual(set(LABS), {"A", "B", "C", "D"})
        for lab in LABS.values():
            for field in ("name", "objective", "status", "disposition", "evidence", "host", "required_capabilities", "dependencies", "fixtures", "stop_conditions", "restoration"):
                with self.subTest(lab=lab["name"], field=field):
                    self.assertIn(field, lab)
            self.assertTrue((ROOT / lab["evidence"]).is_file())

    def test_probe_a_remains_complete_and_independent_labs_continue(self):
        lab = LABS["A"]
        self.assertEqual(lab["status"], "COMPLETE")
        self.assertEqual(lab["disposition"], "CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT")
        self.assertEqual(lab["operations"]["create"], "NOT_TESTED")
        self.assertEqual(lab["operations"]["cleanup"], "NOT_TESTED")
        self.assertEqual(lab["independent_labs_continue"], ["B", "C", "D"])

    def test_current_runtime_gaps_are_not_promoted_to_qualification(self):
        self.assertEqual(LABS["B"]["operations"]["provision"], "NOT_TESTED")
        self.assertEqual(LABS["B"]["feasibility"]["wiqd_direct_user_sharing"], "DOCUMENTED_NOT_RUNTIME_QUALIFIED")
        self.assertEqual(LABS["C"]["disposition"], "RUNTIME_NOT_TESTED")
        self.assertEqual(LABS["D"]["operations"]["retrieve"], "NOT_TESTED")
        self.assertEqual(LABS["D"]["disposition"], "CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT")

    def test_lab_c_source_qualified_contract_never_promotes_runtime(self):
        lab_c = LABS["C"]
        local_audit = lab_c["local_fixture_contract_audit"]
        audit = json.loads((ROOT / local_audit["evidence"]).read_text())

        self.assertEqual(local_audit["fixture_contract_state"], "SOURCE_QUALIFIED")
        self.assertEqual(local_audit["fixture_runtime_state"], "NOT_TESTED")
        self.assertEqual(local_audit["runtime_context_transfer"], "NOT_TESTED")
        self.assertEqual(lab_c["status"], "RUNTIME_NOT_TESTED")
        self.assertEqual(lab_c["runtime_context_transfer"], "NOT_TESTED")
        self.assertEqual(audit["fixture_contract_state"], "SOURCE_QUALIFIED")
        self.assertEqual(audit["runtime_context_transfer"], "NOT_TESTED")
        self.assertEqual(audit["all_fixture_runtime_results"], "NOT_TESTED")
        self.assertEqual(audit["observed_evidence"]["prompts_sent"], 0)
        self.assertEqual(audit["observed_evidence"]["source_content_queries"], 0)
        self.assertFalse(audit["observed_evidence"]["declared_tool_invoked"])
        self.assertFalse(audit["observed_evidence"]["agent_modified"])
        self.assertFalse(audit["observed_evidence"]["tenant_mutation"])
        self.assertFalse(audit["runtime_preconditions"]["complete_effective_knowledge_scope_established"])
        self.assertEqual(audit["runtime_preconditions"]["host_fact_absence_from_corpus"], "NOT_VERIFIED")

        fixtures = {next(iter(item)): next(iter(item.values())) for item in lab_c["fixtures"]}
        self.assertIn("host citation", fixtures["Positive"])
        self.assertIn("absent from the agent knowledge", fixtures["Positive"])
        self.assertIn("absent from host context and agent knowledge", fixtures["Unsupported"])
        self.assertIn("no guessed owner", fixtures["Unsupported"])
        self.assertIn("safe non-disclosure and no action", fixtures["Boundary"])

    def test_qualification_checkpoint_records_target_gate_without_auth_state(self):
        lab_b = LABS["B"]
        self.assertEqual(lab_b["status"], "PREFLIGHT_BLOCKED")
        self.assertEqual(lab_b["target_gate"], "UNQUALIFIED")
        self.assertFalse(lab_b["create_allowed"])
        self.assertEqual(lab_b["operations"]["provision"], "NOT_TESTED")
        self.assertEqual(lab_b["operations"]["share"], "NOT_TESTED")
        preflight = json.loads((ROOT / lab_b["preflight_evidence"]).read_text())
        self.assertEqual(preflight["qualification_state"], "PREFLIGHT_BLOCKED")
        self.assertEqual(preflight["target_gate"], "UNQUALIFIED")
        self.assertFalse(preflight["create_allowed"])
        self.assertFalse(preflight["cloud_resources_created"])

        registry = load_yaml(ROOT / "config/capability-registry.yaml")
        registry_lab = registry["execution_routing"]["capability_evidence_notes"]["lab_b_declarative_agent"]
        self.assertEqual(registry_lab["spec_record"], lab_b["active_specification"]["path"])
        self.assertEqual(registry_lab["spec_identity_source"], "config/qualification-labs.yaml#labs.B.active_specification")
        self.assertEqual(registry_lab["target_gate"], "UNQUALIFIED")
        self.assertFalse(registry_lab["create_allowed"])

        self.assertEqual(LABS["C"]["runtime_context_transfer"], "NOT_TESTED")

    def test_lab_b_approval_preserves_bytes_and_blocks_failed_preflight(self):
        active = LABS["B"]["active_specification"]
        historical = active["supersedes"]
        prior = historical["prior_historical_specification"]
        self.assertEqual(active["path"], "docs/qualification-labs/lab-b-corporate-tenant-spec.md")
        self.assertEqual(active["approval_status"], "APPROVED")
        self.assertTrue(active["active"])
        self.assertEqual(active["approval_applies_to"], "IMMUTABLE_FILE_BYTES")
        spec_bytes = (ROOT / active["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(spec_bytes).hexdigest(), active["sha256"])
        self.assertEqual(active["sha256"], "0d27ae6d9927b8d12cb3edf29ccdd8882c742812c5d0e9ad8da678f46511dd88")
        active_specs = [active, historical, prior]
        self.assertEqual(sum(item["active"] is True for item in active_specs), 1)
        self.assertFalse(historical["active"])
        self.assertEqual(historical["approval_status"], "SUPERSEDED_AFTER_SANITIZATION")
        self.assertEqual(historical["disposition"], "SUPERSEDED_AFTER_SANITIZATION")
        self.assertIn("transient authentication/browser", historical["reason"])
        self.assertEqual(historical["sha256"], "43afbd15acde0c6129dc5884203bf336d3dc0943c58f470c3265969e3e7ca5f8")
        self.assertFalse(prior["active"])
        self.assertEqual(prior["path"], "docs/qualification-labs/lab-b-disposable-agent-spec.md")
        self.assertEqual(prior["approval_status"], "SUPERSEDED")
        self.assertEqual(prior["sha256"], "739229020d2c1ddda2c367f3d35a139b6f34e8725fca39b8495440df0b55e843")
        preflight = json.loads((ROOT / LABS["B"]["preflight_evidence"]).read_text())
        self.assertEqual(preflight["historical_preflight_spec_sha256"], historical["sha256"])
        self.assertEqual(LABS["B"]["status"], "PREFLIGHT_BLOCKED")
        self.assertEqual(LABS["B"]["target_gate"], "UNQUALIFIED")
        self.assertFalse(LABS["B"]["create_allowed"])
        self.assertFalse(preflight["create_allowed"])
        self.assertFalse(preflight["cloud_resources_created"])
        self.assertEqual(preflight["preflight_gates"]["complete_resource_cleanup_absence_verification"], "UNPROVEN")

    def test_lab_b_spec_keeps_route_and_disposable_scope_explicit(self):
        active = LABS["B"]["active_specification"]
        spec_path = ROOT / active["path"]
        spec_bytes = spec_path.read_bytes()
        spec = spec_bytes.decode()
        self.assertIn("WIQD direct-user sharing", spec)
        self.assertIn("smithr@opentext.com", spec)
        self.assertIn("AF-B-UNIT-42", spec)
        self.assertIn("What room is qualification marker AF-B-UNIT-42 assigned to?", spec)
        self.assertIn("SHARE only to smithr@opentext.com", spec)
        self.assertIn("fresh read-only lookup proving that ID absent", spec)
        self.assertIn("Azure subscription access if provisioning requires it", spec)
        self.assertIn("**Specification status:** `APPROVED`", spec)
        self.assertIn("**Execution state:** `PREFLIGHT_BLOCKED`; `TARGET_GATE=UNQUALIFIED`; `CREATE_ALLOWED=NO`.", spec)
        header = spec.split("##", maxsplit=1)[0].lower()
        self.assertEqual(active["approval_status"], "APPROVED")
        self.assertTrue(active["active"])
        self.assertNotRegex(header, r"\b(proposed|designed|not approved)\b")
        self.assertNotIn("restricted-context status check", spec)
        self.assertNotIn("Chrome Stable's `AgentFactory` profile", spec)
        self.assertNotIn("WIQD core signed in", spec)
        self.assertEqual(
            hashlib.sha256(spec_bytes).hexdigest(),
            LABS["B"]["active_specification"]["sha256"],
        )


if __name__ == "__main__":
    unittest.main()
