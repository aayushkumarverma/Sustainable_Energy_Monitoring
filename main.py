
"""End-to-end orchestrator: sensor simulation -> twin -> advice -> projection."""

from simulator import generate_telemetry
from digital_twin import calculate_footprint, simulate_reduction
from ai_optimizer import get_ai_suggestions


def run_simulation(
    scenario="normal",
    emission_factor=0.70,
    electricity_rate=8.0,
    seed=None
):
    # 1. Generate simulated machine data
    telemetry = generate_telemetry(
        scenario=scenario,
        seed=seed
    )

    # 2. Calculate baseline energy consumption
    baseline = calculate_footprint(
        telemetry,
        emission_factor,
        electricity_rate
    )

    # 3. Obtain AI optimization recommendations
    recommendation = get_ai_suggestions(baseline)

    reduction_pct = float(
        recommendation["recommended_power_reduction_pct"]
    )

    # Safety check: block optimization if overheating
    if (
        baseline["cv_anomaly"]
        or recommendation.get("requires_inspection")
    ):
        reduction_pct = 0.0
        recommendation["recommended_power_reduction_pct"] = 0.0

    # 4. Run virtual optimization simulation
    optimized = simulate_reduction(
        baseline,
        reduction_pct
    )

    # 5. Calculate projected savings
    savings = {
        "energy_kwh": round(
            baseline["energy_kwh"] - optimized["energy_kwh"], 2
        ),
        "carbon_kg": round(
            baseline["carbon_kg"] - optimized["carbon_kg"], 2
        ),
        "cost_inr": round(
            baseline["cost_inr"] - optimized["cost_inr"], 2
        )
    }

    # 6. Return complete data for dashboard
    return {
        "telemetry": telemetry,
        "baseline": baseline,
        "recommendation": recommendation,
        "optimized": optimized,
        "savings": savings
    }


if __name__ == "__main__":
    result = run_simulation(scenario="normal", seed=42)

    before = result["baseline"]
    after = result["optimized"]
    advice = result["recommendation"]

    print("\n=== ECOTWIN AI — SIMULATED IMPACT REPORT ===")

    print(f"Machine: {before['machine_id']}")
    print(f"Status: {before['status']}")
    print(f"Thermal anomaly: {before['cv_anomaly']}")

    print(f"\nRecommendation source: {advice['source']}")
    print(f"Action: {advice['action']}")
    print(
        f"Reduction target: "
        f"{advice['recommended_power_reduction_pct']:.1f}%"
    )

    print(
        f"\nBaseline: {before['energy_kwh']:.2f} kWh | "
        f"{before['carbon_kg']:.2f} kg CO2e"
    )

    print(
        f"Projected: {after['energy_kwh']:.2f} kWh | "
        f"{after['carbon_kg']:.2f} kg CO2e"
    )

    print(
        f"Estimated carbon savings: "
        f"{result['savings']['carbon_kg']:.2f} kg CO2e"
    )

    print(
        "\nNote: Savings are simulated, not physically verified."
    )
