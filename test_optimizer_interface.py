
import json
from ai_optimizer import get_ai_suggestions

sample_data = {
    "machine_id": "M_001",
    "power_kwh": 45.2,
    "runtime_hours": 8.0,
    "temperature_c": 72.5,
    "status": "active",
    "carbon_kg": 31.64,
    "estimated_energy_waste_kwh": 2.26,
}

result = get_ai_suggestions(sample_data)

assert isinstance(result, dict), "Output must be a dictionary"
assert result["machine_id"] == "M_001"
assert "recommended_power_reduction_pct" in result
assert result["provider"] in {"gemini", "demo_fallback"}
assert result["status"] in {"success", "fallback"}
assert result["requires_validation"] is True

print("Optimizer interface test passed.")
print(json.dumps(result, indent=2))
