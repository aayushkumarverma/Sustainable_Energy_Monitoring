
import os
import json
import math
from typing import Any

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_REDUCTION_PCT = 15.0

ALLOWED_ACTIONS = {
    "reduce_idle_time",
    "shift_flexible_load",
    "inspect_efficiency",
    "no_change",
}

ALLOWED_CONFIDENCE = {"low", "medium", "high"}

NUMERIC_FIELDS = (
    "energy_consumed_kwh",
    "power_kwh",
    "energy_kwh",
    "runtime_hours",
    "temperature_c",
    "carbon_kg",
    "estimated_energy_waste_kwh",
)


def validate_recommendation(result: dict) -> dict:
    """Validate an AI recommendation before it is used."""

    if not isinstance(result, dict):
        raise ValueError("AI output must be a dictionary.")

    required_fields = {
        "machine_id",
        "action",
        "recommended_power_reduction_pct",
        "summary",
        "reason",
        "confidence",
    }

    missing = required_fields - result.keys()
    if missing:
        raise ValueError(
            f"Missing fields: {', '.join(sorted(missing))}"
        )

    if (
        not isinstance(result["machine_id"], str)
        or not result["machine_id"].strip()
    ):
        raise ValueError("machine_id must be a non-empty string.")

    if result["action"] not in ALLOWED_ACTIONS:
        raise ValueError("Invalid optimization action.")

    if result["confidence"] not in ALLOWED_CONFIDENCE:
        raise ValueError("Invalid confidence value.")

    for field in ("summary", "reason"):
        if (
            not isinstance(result[field], str)
            or not result[field].strip()
        ):
            raise ValueError(f"{field} must be a non-empty string.")

    reduction_value = result["recommended_power_reduction_pct"]

    if isinstance(reduction_value, bool):
        raise ValueError("Reduction percentage must be numeric.")

    try:
        reduction = float(reduction_value)
    except (TypeError, ValueError):
        raise ValueError("Invalid reduction percentage.") from None

    if not math.isfinite(reduction):
        raise ValueError("Reduction must be finite.")

    if not 0 <= reduction <= MAX_REDUCTION_PCT:
        raise ValueError("Reduction must be between 0 and 15 percent.")

    if result["action"] in {"inspect_efficiency", "no_change"}:
        if reduction != 0:
            raise ValueError(
                "Inspection and no_change must use zero reduction."
            )

    result["recommended_power_reduction_pct"] = reduction
    result["requires_validation"] = True

    return result


def demo_fallback(machine_id: str, reason: str) -> dict:
    """Provide a safe, clearly labeled recommendation if AI fails."""

    return {
        "machine_id": machine_id,
        "provider": "demo_fallback",
        "status": "fallback",
        "action": "inspect_efficiency",
        "recommended_power_reduction_pct": 0.0,
        "summary": (
            "Inspect machine efficiency and review idle operation."
        ),
        "reason": (
            "Savings have not been established by a validated simulation."
        ),
        "confidence": "low",
        "fallback_reason": reason,
        "requires_validation": True,
    }


def get_ai_suggestions(data_dict: dict[str, Any]) -> dict:
    """
    Analyze simulated machine telemetry using Gemini.

    This function provides recommendations only. It does not
    control physical equipment or verify real-world savings.
    """

    if not isinstance(data_dict, dict):
        raise TypeError("data_dict must be a dictionary.")

    machine_id = str(data_dict.get("machine_id", "")).strip()
    if not machine_id:
        raise ValueError("machine_id is required.")

    # Validate telemetry before sending it to the AI model.
    for field in NUMERIC_FIELDS:
        if field not in data_dict:
            continue

        value = data_dict[field]

        if isinstance(value, bool):
            raise ValueError(f"{field} must be numeric.")

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric.") from None

        if not math.isfinite(number) or number < 0:
            raise ValueError(
                f"{field} must be finite and non-negative."
            )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return demo_fallback(
            machine_id,
            "GEMINI_API_KEY is missing from the environment.",
        )

    try:
        machine_json = json.dumps(data_dict, allow_nan=False)

        prompt = f"""
You are an energy-efficiency advisor for simulated industrial equipment.

Analyze the machine telemetry and recommend cautious, practical actions.
Use only evidence supported by the supplied data.
Do not claim that savings are measured or guaranteed.
Never recommend bypassing safety controls.
If there is a thermal anomaly or insufficient evidence, recommend
inspection or no change, with zero power reduction.

Machine data:
{machine_json}

Return one JSON object with exactly these fields:
{{
  "machine_id": {json.dumps(machine_id)},
  "action": "inspect_efficiency",
  "recommended_power_reduction_pct": 0,
  "summary": "Short explanation",
  "reason": "Evidence supporting the recommendation",
  "confidence": "low"
}}

Allowed actions:
reduce_idle_time, shift_flexible_load, inspect_efficiency, no_change.

Rules:
- Reduction must be a number from 0 to 15.
- Use zero when evidence is insufficient.
- Inspection and no_change must use zero reduction.
- Confidence must be low, medium, or high.
- Return valid JSON only, without Markdown fences.
"""

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        result = json.loads(response.text)

        if not isinstance(result, dict):
            raise ValueError("Gemini did not return a JSON object.")

        if result.get("machine_id") != machine_id:
            raise ValueError("Gemini returned the wrong machine ID.")

        # Prevent power-reduction recommendations when a hotspot
        # or thermal anomaly is reported by the supplied telemetry.
        thermal_anomaly = data_dict.get(
            "thermal_anomaly",
            data_dict.get("requires_inspection", False),
        )

        if thermal_anomaly:
            result["action"] = "inspect_efficiency"
            result["recommended_power_reduction_pct"] = 0

        validated = validate_recommendation(result)
        validated["provider"] = "gemini"
        validated["status"] = "success"

        return validated

    except Exception as error:
        return demo_fallback(
            machine_id,
            f"{type(error).__name__}: {error}",
        )


if __name__ == "__main__":
    sample_data = {
        "machine_id": "M_001",
        "energy_consumed_kwh": 45.2,
        "runtime_hours": 8,
        "temperature_c": 72.5,
        "status": "active",
        "carbon_kg": 31.64,
        "estimated_energy_waste_kwh": 2.26,
    }

    recommendation = get_ai_suggestions(sample_data)
    print(json.dumps(recommendation, indent=2))
