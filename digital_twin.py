"""Digital Twin energy, emissions, cost and virtual optimization calculations."""
import math


def _finite_non_negative(name, value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number") from None
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{name} must be a finite, non-negative number")
    return number


def calculate_footprint(telemetry, emission_factor=0.70, electricity_rate=8.0):
    """Calculate estimated energy use (kWh), emissions (kg CO2e) and cost (INR).

    Assumption: runtime_hours is the operating duration represented by this
    telemetry snapshot. This is simulated data, not a physical measurement.
    """
    required = ("power_kw", "runtime_hours", "temperature_c")
    missing = [key for key in required if key not in telemetry]
    if missing:
        raise KeyError("Telemetry missing required field(s): " + ", ".join(missing))

    power_kw = _finite_non_negative("power_kw", telemetry["power_kw"])
    hours = _finite_non_negative("runtime_hours", telemetry["runtime_hours"])
    temperature = float(telemetry["temperature_c"])
    if not math.isfinite(temperature):
        raise ValueError("temperature_c must be a finite number")
    emission_factor = _finite_non_negative("emission_factor", emission_factor)
    electricity_rate = _finite_non_negative("electricity_rate", electricity_rate)

    energy_kwh = power_kw * hours
    carbon_kg = energy_kwh * emission_factor
    cost_inr = energy_kwh * electricity_rate

    # Transparent illustrative score: starts at 100, with temperature and
    # warning-state penalties. It is a demo indicator, not measured efficiency.
    heat_penalty = max(0.0, temperature - 60.0) * 0.7
    status = str(telemetry.get("status", "Running")).lower()
    status_penalty = 15.0 if status == "warning" else 0.0
    if bool(telemetry.get("cv_anomaly", telemetry.get("anomaly_detected", False))):
        status_penalty += 15.0
    efficiency_score = max(0.0, min(100.0, 100.0 - heat_penalty - status_penalty))

    return {
        **telemetry,
        "power_kw": round(power_kw, 4),
        "runtime_hours": round(hours, 4),
        "energy_kwh": round(energy_kwh, 2),
        "carbon_kg": round(carbon_kg, 2),
        "cost_inr": round(cost_inr, 2),
        "efficiency_score": round(efficiency_score, 1),
        "emission_factor_used": emission_factor,
        "electricity_rate_used": electricity_rate,
    }


def simulate_reduction(baseline, reduction_pct):
    """Project lower power at the same runtime; accepts a maximum 25% reduction."""
    reduction_pct = float(reduction_pct)
    if not math.isfinite(reduction_pct) or not 0.0 <= reduction_pct <= 25.0:
        raise ValueError("Reduction must be between 0% and 25%")

    updated = dict(baseline)
    updated["power_kw"] = round(
        float(baseline["power_kw"]) * (1.0 - reduction_pct / 100.0), 4
    )
    updated["projected_reduction_pct"] = reduction_pct
    # Recalculate based on the same duration and tariff/emission assumptions.
    return calculate_footprint(
        updated,
        emission_factor=baseline["emission_factor_used"],
        electricity_rate=baseline["electricity_rate_used"],
    )


if __name__ == "__main__":
    sample = {
        "machine_id": "M_001", "machine_type": "Chiller",
        "status": "Running", "power_kw": 6.0,
        "runtime_hours": 8.0, "temperature_c": 66.0,
        "cv_anomaly": False,
    }
    before = calculate_footprint(sample)
    after = simulate_reduction(before, 15.0)
    print("Baseline:", before)
    print("Projected:", after)
    print("Energy saved (kWh):", round(before["energy_kwh"] - after["energy_kwh"], 2))
