
import unittest

from ai_optimizer import (
    validate_recommendation,
    demo_fallback,
    get_ai_suggestions,
)


class TestAIOptimizer(unittest.TestCase):

    def test_valid_recommendation(self):
        result = {
            "machine_id": "M_001",
            "action": "reduce_idle_time",
            "recommended_power_reduction_pct": 5,
            "summary": "Reduce unnecessary idle operation.",
            "reason": "Idle time may be avoidable.",
            "confidence": "medium",
        }

        validated = validate_recommendation(result)

        self.assertEqual(validated["machine_id"], "M_001")
        self.assertEqual(
            validated["recommended_power_reduction_pct"], 5
        )
        self.assertTrue(validated["requires_validation"])

    def test_inspection_cannot_claim_power_reduction(self):
        result = {
            "machine_id": "M_001",
            "action": "inspect_efficiency",
            "recommended_power_reduction_pct": 5,
            "summary": "Inspect equipment.",
            "reason": "Possible energy waste.",
            "confidence": "medium",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_rejects_excessive_reduction(self):
        result = {
            "machine_id": "M_001",
            "action": "reduce_idle_time",
            "recommended_power_reduction_pct": 25,
            "summary": "Reduce idle time.",
            "reason": "Excessive reduction for testing.",
            "confidence": "low",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_rejects_invalid_action(self):
        result = {
            "machine_id": "M_001",
            "action": "shut_down_safety_system",
            "recommended_power_reduction_pct": 5,
            "summary": "Invalid action.",
            "reason": "Testing invalid actions.",
            "confidence": "low",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_no_change_requires_zero_reduction(self):
        result = {
            "machine_id": "M_001",
            "action": "no_change",
            "recommended_power_reduction_pct": 5,
            "summary": "No change required.",
            "reason": "Testing the no-change action.",
            "confidence": "medium",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_fallback_is_labeled(self):
        result = demo_fallback("M_001", "Test error")

        self.assertEqual(result["provider"], "demo_fallback")
        self.assertEqual(result["status"], "fallback")
        self.assertEqual(
            result["recommended_power_reduction_pct"], 0.0
        )
        self.assertTrue(result["requires_validation"])

    def test_missing_machine_id_is_rejected(self):
        with self.assertRaises(ValueError):
            get_ai_suggestions({"energy_consumed_kwh": 10})

    def test_negative_energy_is_rejected(self):
        with self.assertRaises(ValueError):
            get_ai_suggestions({
                "machine_id": "M_001",
                "energy_consumed_kwh": -10,
            })

    def test_rejects_missing_fields(self):
        result = {
            "machine_id": "M_001",
            "action": "reduce_idle_time",
            "recommended_power_reduction_pct": 5,
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_rejects_nan_reduction(self):
        result = {
            "machine_id": "M_001",
            "action": "reduce_idle_time",
            "recommended_power_reduction_pct": float("nan"),
            "summary": "Test recommendation.",
            "reason": "Test reason.",
            "confidence": "low",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)

    def test_rejects_boolean_reduction(self):
        result = {
            "machine_id": "M_001",
            "action": "reduce_idle_time",
            "recommended_power_reduction_pct": True,
            "summary": "Test recommendation.",
            "reason": "Test reason.",
            "confidence": "low",
        }

        with self.assertRaises(ValueError):
            validate_recommendation(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
