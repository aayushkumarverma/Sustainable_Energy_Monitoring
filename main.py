
"""End-to-end orchestrator for EcoTwin AI.

Pipeline:
Simulator -> Digital Twin -> AI Recommendation -> Savings Projection

Note: This is a simulation and does not control physical equipment.
"""

from simulator import generate_telemetry
from digital_twin import calculate_footprint, simulate_reduction
from ai_optimizer import get_ai_suggestions


def run_simulation(
    scenario="normal",
    emission_factor=0.70,
    electricity_rate=8.0,
    seed=None,
):
    """Run a simulation and return telemetry, recommendation, and projections."""

    # Step 1: Generate simulated machine telemetry.
    telemetry = generate_telemetry(
        scenario=scenario,
        seed=seed,
    )

    # Step 2: Calculate baseline energy, carbon, and cost.
    baseline = calculate_footprint(
        telemetry,
        emission_factor=emission_factor,
        electricity_rate=electricity_rate,
    )

    # Step 3: Request an AI recommendation.
    recommendation = get_ai_suggestions(baseline)

    # Safely parse the proposed reduction.
    try:
        reduction_pct = float(
            recommendation.get("recommended_power_reduction_pct", 0.0)
        )
    except (TypeError, ValueError):
        reduction_pct = 0.0

    # Step 4: Apply a safety hold when inspection is required
    # or a thermal anomaly is detected.
    thermal_anomaly = bool(
        baseline.get(
            "cv_anomaly",
            baseline.get("anomaly_detected", False),
        )
    )

    requires_inspection = bool(
        recommendation.get("requires_inspection", False)
    )

    # Do not apply invalid or unsafe reductions.
    if (
        thermal_anomaly
        or requires_inspection
        or reduction_pct < 0
        or reduction_pct > 15
    ):
        reduction_pct = 0.0
        recommendation["recommended_power_reduction_pct"] = 0.0
        recommendation["requires_inspection"] = True

    # Step 5: Calculate the hypothetical optimized scenario.
    optimized = simulate_reduction(
        baseline,
        reduction_pct,
    )

    # Step 6: Calculate simulated savings.
    savings = {
        "energy_kwh": round(
            baseline["energy_kwh"] - optimized["energy_kwh"], 2
        ),
        "carbon_kg": round(
            baseline["carbon_kg"] - optimized["carbon_kg"], 2
        ),
        "cost_inr": round(
            baseline["cost_inr"] - optimized["cost_inr"], 2
        ),
    }

    return {
        "telemetry": telemetry,
        "baseline": baseline,
        "recommendation": recommendation,
        "optimized": optimized,
        "savings": savings,
    }


def print_simulation_report(result):
    """Print a readable report from a simulation result."""

    baseline = result["baseline"]
    optimized = result["optimized"]
    advice = result["recommendation"]
    savings = result["savings"]

    source = advice.get(
        "provider",
        advice.get("source", "Unknown"),
    )

    thermal_anomaly = bool(
        baseline.get(
            "cv_anomaly",
            baseline.get("anomaly_detected", False),
        )
    )

    print("\n=== ECOTWIN AI — SIMULATED IMPACT REPORT ===")
    print(f"Machine: {baseline.get('machine_id', 'Unknown')}")
    print(f"Status: {baseline.get('status', 'Unknown')}")
    print(f"Thermal anomaly: {thermal_anomaly}")
    print(f"Recommendation source: {source}")
    print(f"Action: {advice.get('action', 'No recommendation')}")
    print(
        "Reduction target: "
        f"{advice.get('recommended_power_reduction_pct', 0.0):.1f}%"
    )

    print(
        f"\nBaseline: {baseline['energy_kwh']:.2f} kWh | "
        f"{baseline['carbon_kg']:.2f} kg CO2e"
    )
    print(
        f"Projected: {optimized['energy_kwh']:.2f} kWh | "
        f"{optimized['carbon_kg']:.2f} kg CO2e"
    )
    print(f"Estimated energy savings: {savings['energy_kwh']:.2f} kWh")
    print(f"Estimated carbon savings: {savings['carbon_kg']:.2f} kg CO2e")
    print(f"Estimated cost savings: ₹{savings['cost_inr']:.2f}")

    if advice.get("requires_inspection", False):
        print("Safety note: Inspection is required before optimization.")

    if advice.get("status") == "fallback":
        print("AI note: Gemini was unavailable; a fallback was used.")

    print("\nNote: Savings are simulated, not physically verified.")


if __name__ == "__main__":
    simulation_result = run_simulation(
        scenario="normal",
        seed=42,
    )
    print_simulation_report(simulation_result)
