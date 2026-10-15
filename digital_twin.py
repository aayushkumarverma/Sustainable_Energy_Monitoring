
def calculate_footprint(
    telemetry,
    emission_factor=0.70,
    electricity_rate=8.0
):
    """Calculate energy, carbon emissions and cost."""

    power_kw = float(telemetry["power_kw"])
    hours = float(telemetry["runtime_hours"])

    if min(
        power_kw,
        hours,
        emission_factor,
        electricity_rate
    ) < 0:
        raise ValueError("Values cannot be negative")

    # Energy consumption
    energy_kwh = power_kw * hours

    # Estimated emissions
    carbon_kg = energy_kwh * emission_factor

    # Estimated electricity cost
    cost_inr = energy_kwh * electricity_rate

    # Illustrative operational score
    temperature = float(
        telemetry["temperature_c"]
    )

    heat_penalty = max(
        0.0,
        temperature - 60.0
    ) * 0.8

    load_penalty = power_kw * 1.5

    efficiency_score = max(
        0.0,
        100.0 - heat_penalty - load_penalty
    )

    return {
        **telemetry,
        "energy_kwh": round(energy_kwh, 2),
        "carbon_kg": round(carbon_kg, 2),
        "cost_inr": round(cost_inr, 2),
        "efficiency_score": round(
            efficiency_score, 1
        ),
        "emission_factor_used": float(
            emission_factor
        ),
        "electricity_rate_used": float(
            electricity_rate
        )
    }


def simulate_reduction(baseline, reduction_pct):
    """Simulate reduced power consumption."""

    reduction_pct = float(reduction_pct)

    if not 0 <= reduction_pct <= 25:
        raise ValueError(
            "Reduction must be between 0% and 25%"
        )

    updated = dict(baseline)

    # Apply projected reduction to average power
    updated["power_kw"] = round(
        baseline["power_kw"]
        * (1 - reduction_pct / 100),
        4
    )

    # Recalculate emissions and energy
    return calculate_footprint(
        updated,
        emission_factor=baseline[
            "emission_factor_used"
        ],
        electricity_rate=baseline[
            "electricity_rate_used"
        ]
    )


if __name__ == "__main__":

    sample = {
        "machine_id": "M_001",
        "power_kw": 6.0,
        "runtime_hours": 8.0,
        "temperature_c": 66.0,
        "cv_anomaly": False
    }

    before = calculate_footprint(sample)

    after = simulate_reduction(
        before,
        reduction_pct=15.0
    )

    print("Baseline:", before)
    print("Projected:", after)
