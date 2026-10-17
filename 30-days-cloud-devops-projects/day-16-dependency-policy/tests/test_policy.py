import copy
import json
import unittest
from pathlib import Path

from check import evaluate, main, markdown


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = json.loads((ROOT / "inventory.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))


class PolicyTests(unittest.TestCase):
    def test_risky_inventory_blocks_with_expected_codes(self):
        report = evaluate(INVENTORY, POLICY)
        self.assertEqual(report["decision"], "BLOCK")
        self.assertEqual(report["summary"], {"components": 6, "blocked_components": 3, "findings": 4})
        self.assertEqual({f["code"] for f in report["findings"]}, {"BLOCKED_LICENSE", "STALE_REVIEW", "MISSING_OWNER"})
        self.assertIn("## Findings", markdown(report))

    def test_clean_inventory_passes(self):
        clean = json.loads((ROOT / "inventory-clean.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluate(clean, POLICY)["decision"], "PASS")
        self.assertEqual(main([str(ROOT / "inventory-clean.json")]), 0)

    def test_license_matching_is_case_insensitive(self):
        inventory = copy.deepcopy(INVENTORY)
        inventory["packages"][0]["license"] = "unknown"
        codes = evaluate(inventory, POLICY)["components"][0]["finding_codes"]
        self.assertIn("BLOCKED_LICENSE", codes)

    def test_review_boundary(self):
        inventory = copy.deepcopy(INVENTORY)
        inventory["packages"] = [inventory["packages"][0]]
        inventory["packages"][0]["last_reviewed"] = "2025-10-17"
        self.assertEqual(evaluate(inventory, POLICY)["decision"], "PASS")
        inventory["packages"][0]["last_reviewed"] = "2025-10-16"
        self.assertEqual(evaluate(inventory, POLICY)["findings"][0]["code"], "STALE_REVIEW")

    def test_missing_owner_can_be_disabled(self):
        inventory = copy.deepcopy(INVENTORY)
        inventory["packages"] = [inventory["packages"][3]]
        policy = {**POLICY, "require_owner": False}
        self.assertEqual(evaluate(inventory, policy)["decision"], "PASS")

    def test_duplicate_component_rejected(self):
        inventory = copy.deepcopy(INVENTORY)
        inventory["packages"].append(copy.deepcopy(inventory["packages"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate(inventory, POLICY)

    def test_future_review_rejected(self):
        inventory = copy.deepcopy(INVENTORY)
        inventory["packages"][0]["last_reviewed"] = "2026-10-18"
        with self.assertRaisesRegex(ValueError, "after as_of"):
            evaluate(inventory, POLICY)

    def test_invalid_policy_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            evaluate(INVENTORY, {**POLICY, "maximum_review_age_days": -1})
        with self.assertRaisesRegex(ValueError, "boolean"):
            evaluate(INVENTORY, {**POLICY, "require_owner": "yes"})

    def test_invalid_cli_returns_input_error(self):
        self.assertEqual(main([str(ROOT / "does-not-exist.json")]), 2)


if __name__ == "__main__":
    unittest.main()
