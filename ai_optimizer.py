
import json
import os

from dotenv import load_dotenv

load_dotenv()


def _local_recommendation(
    note="No Gemini API key configured"
):
    """Clearly labeled demo fallback."""

    return {
        "recommended_power_reduction_pct": 15.0,
        "action": (
            "Trial a 15% fan-speed setpoint reduction "
            "during low-demand periods; verify comfort "
            "and equipment limits."
        ),
        "reasoning": (
            "This is an illustrative adjustment, "
            "not a validated machine-specific saving."
        ),
        "confidence_score": None,
        "requires_inspection": False,
        "source": "Local demonstration rule (not Gemini)",
        "note": note
    }


def get_ai_suggestions(baseline):
    """Get optimization suggestions with safety checks."""

    # SAFETY OVERRIDE

    if (
        baseline.get("cv_anomaly")
        or float(
            baseline.get("temperature_c", 0)
        ) > 82
    ):
        return {
            "recommended_power_reduction_pct": 0.0,
            "action": (
                "Inspect the thermal hotspot and verify "
                "cooling and equipment safety before "
                "attempting optimization."
            ),
            "reasoning": (
                "The simulated thermal image indicates "
                "an abnormal hotspot. Equipment safety "
                "takes priority over energy reduction."
            ),
            "confidence_score": None,
            "requires_inspection": True,
            "source": "Rule-based safety override",
            "note": (
                "Optimization blocked until "
                "the anomaly is resolved."
            )
        }

    # API KEY

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        return _local_recommendation()

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key
        )

        # Prepare only useful telemetry
        inputs = {
            k: baseline[k]
            for k in (
                "machine_id",
                "power_kw",
                "runtime_hours",
                "energy_kwh",
                "temperature_c",
                "cv_anomaly",
                "carbon_kg"
            )
            if k in baseline
        }

        prompt = f"""
You are an industrial HVAC sustainability advisor
working within a DEMONSTRATION digital twin.

Analyze this telemetry:

{json.dumps(inputs, indent=2)}

Recommend ONE realistic energy-saving action.

Rules:
- Recommend a reduction from 0% to 25%.
- Zero is acceptable when optimization is unsuitable.
- Do not claim that recommendations are guaranteed safe.
- Do not claim that savings have been physically verified.
- Give a concise engineering justification.

Return only JSON containing these keys:

recommended_power_reduction_pct: number
action: string
reasoning: string
confidence_score: number or null

Confidence is a self-assessment, not a calibrated probability.
"""

        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-flash-latest"
            ),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        suggestion = json.loads(
            response.text or "{}"
        )

        # VALIDATION

        pct = float(
            suggestion["recommended_power_reduction_pct"]
        )

        if not 0 <= pct <= 25:
            raise ValueError(
                "Reduction outside allowed range"
            )

        action = str(
            suggestion["action"]
        ).strip()

        reasoning = str(
            suggestion["reasoning"]
        ).strip()

        if not action or not reasoning:
            raise ValueError("Incomplete AI response")

        return {
            "recommended_power_reduction_pct": pct,
            "action": action,
            "reasoning": reasoning,
            "confidence_score": suggestion.get(
                "confidence_score"
            ),
            "requires_inspection": False,
            "source": "Google Gemini",
            "note": (
                "AI advice is unverified; "
                "demonstration only."
            )
        }

    except Exception as error:
        return _local_recommendation(
            f"Gemini unavailable "
            f"({type(error).__name__}); "
            f"local demo rule used."
        )


if __name__ == "__main__":

    sample = {
        "machine_id": "M_001",
        "power_kw": 6.0,
        "runtime_hours": 8.0,
        "energy_kwh": 48.0,
        "temperature_c": 65.0,
        "cv_anomaly": False,
        "carbon_kg": 33.6
    }

    print(get_ai_suggestions(sample))
