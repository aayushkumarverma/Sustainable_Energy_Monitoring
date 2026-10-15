
import numpy as np

HOTSPOT_THRESHOLD_C = 82.0


def analyze_thermal_feed(thermal_matrix):
    """Detect thermal anomalies in a simulated camera image."""

    pixels = np.asarray(thermal_matrix, dtype=float)

    max_temp = float(pixels.max())

    hot_pixels = int(
        np.count_nonzero(pixels > HOTSPOT_THRESHOLD_C)
    )

    anomaly = hot_pixels >= 2

    # Heuristic detection score, not ML confidence
    if anomaly:
        score = min(0.99, 0.75 + 0.025 * hot_pixels)
    else:
        score = min(
            0.99,
            0.80 + max(0, HOTSPOT_THRESHOLD_C - max_temp) / 100
        )

    return round(max_temp, 2), anomaly, round(score, 2)


def generate_telemetry(scenario="normal", seed=None):
    """Generate machine telemetry and simulated thermal data."""

    if scenario not in ("normal", "overheating"):
        raise ValueError("Invalid scenario")

    rng = np.random.default_rng(seed)

    # Generate normal thermal image
    heatmap = rng.normal(
        loc=59 if scenario == "normal" else 66,
        scale=3.0,
        size=(8, 8)
    )

    # Add a hotspot for the overheating scenario
    if scenario == "overheating":
        heatmap[2:5, 3:6] = rng.normal(
            loc=90,
            scale=2,
            size=(3, 3)
        )

    # Run simulated thermal inspection
    max_temp, anomaly, score = analyze_thermal_feed(heatmap)

    # Generate machine power consumption
    power_kw = round(float(rng.uniform(5.0, 8.0)), 2)

    # Generate machine operating hours
    runtime_hours = round(float(rng.uniform(6.0, 12.0)), 2)

    return {
        "machine_id": "IND-HVAC-01",
        "power_kw": power_kw,
        "runtime_hours": runtime_hours,
        "temperature_c": max_temp,
        "status": "warning" if anomaly else "normal",
        "cv_anomaly": anomaly,
        "cv_confidence": score,
        "thermal_heatmap": np.round(heatmap, 2).tolist()
    }


if __name__ == "__main__":
    print(generate_telemetry(scenario="normal", seed=42))
