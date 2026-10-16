"""Synthetic machine telemetry and thermal-hotspot simulator for EcoTwin AI.

This is a demonstration simulator, not a connection to physical equipment.
It preserves Member 2's MachineSimulator API and adds the generate_telemetry()
function expected by Member 1's main.py.
"""
from datetime import datetime
import random
import numpy as np


class MachineSimulator:
    def __init__(self, machine_id="Machine-01", machine_type="Chiller",
                 grid_size=8, anomaly_threshold=82.0):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.grid_size = int(grid_size)
        self.anomaly_threshold = float(anomaly_threshold)
        self.profiles = {
            "Chiller": {"base_power": 45.0, "base_temp": 68.0, "max_temp": 90.0},
            "Furnace": {"base_power": 90.0, "base_temp": 82.0, "max_temp": 110.0},
            "Compressor": {"base_power": 30.0, "base_temp": 55.0, "max_temp": 75.0},
        }
        self.config = self.profiles.get(machine_type, self.profiles["Chiller"])
        self.history = []
        self.max_history_length = 20

    def step(self, scenario="normal"):
        """Generate one synthetic reading and append it to the rolling history."""
        scenario = str(scenario).lower()
        if scenario not in {"normal", "overheating"}:
            raise ValueError("scenario must be 'normal' or 'overheating'")

        if scenario == "overheating":
            status = "Warning"
            power_kw = round(self.config["base_power"] * random.uniform(1.2, 1.4), 2)
            temperature_c = round(max(self.config["base_temp"] * 1.2, 88.0), 2)
        else:
            status = random.choices(
                ["Running", "Idle", "Warning"], weights=[0.80, 0.15, 0.05]
            )[0]
            if status == "Running":
                power_kw = round(self.config["base_power"] * random.uniform(0.9, 1.1), 2)
                temperature_c = round(self.config["base_temp"] * random.uniform(0.95, 1.05), 2)
            elif status == "Warning":
                power_kw = round(self.config["base_power"] * random.uniform(1.2, 1.4), 2)
                temperature_c = round(self.config["base_temp"] * random.uniform(1.15, 1.3), 2)
            else:
                power_kw = round(self.config["base_power"] * 0.1, 2)
                temperature_c = round(self.config["base_temp"] * 0.6, 2)

        # One snapshot represents an illustrative 8-hour operating window.
        # Change this if your team defines a different measurement interval.
        runtime_hours = 8.0
        heatmap = self._generate_thermal_heatmap(temperature_c, force_hotspot=(scenario == "overheating"))
        anomaly_data = self._detect_thermal_anomalies(heatmap)

        record = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "machine_id": self.machine_id,
            "machine_type": self.machine_type,
            "status": status,
            "power_kw": float(power_kw),
            "runtime_hours": float(runtime_hours),
            "temperature_c": float(temperature_c),
            "thermal_heatmap": heatmap.tolist(),
            # Canonical field expected by main.py:
            "cv_anomaly": bool(anomaly_data["anomaly_detected"]),
            "cv_confidence": float(anomaly_data["cv_confidence"]),
            # Member 2's original names are preserved for compatibility:
            "anomaly_detected": bool(anomaly_data["anomaly_detected"]),
            "hotspot_count": int(anomaly_data["hotspot_count"]),
            "hotspot_zones": anomaly_data["hotspot_zones"],
            "bounding_boxes": anomaly_data["bounding_boxes"],
            "anomaly_threshold_c": self.anomaly_threshold,
        }

        self.history.append(record)
        if len(self.history) > self.max_history_length:
            self.history.pop(0)
        return record

    def get_history(self):
        return list(self.history)

    def _generate_thermal_heatmap(self, base_temp, force_hotspot=False):
        heatmap = np.random.normal(
            loc=float(base_temp) - 4.0, scale=2.0,
            size=(self.grid_size, self.grid_size)
        )
        if force_hotspot or base_temp > 75.0 or random.random() < 0.4:
            hx = random.randint(1, max(1, self.grid_size - 3))
            hy = random.randint(1, max(1, self.grid_size - 3))
            heatmap[hx:hx+2, hy:hy+2] += random.uniform(12.0, 22.0)
        return np.clip(heatmap, 20.0, 120.0)

    def _detect_thermal_anomalies(self, heatmap):
        grid = np.asarray(heatmap, dtype=float)
        indices = np.argwhere(grid > self.anomaly_threshold)
        zones, boxes = [], []
        for r, c in indices:
            vertical = "Top" if r < self.grid_size / 3 else (
                "Bottom" if r >= 2 * self.grid_size / 3 else "Center"
            )
            horizontal = "Left" if c < self.grid_size / 3 else (
                "Right" if c >= 2 * self.grid_size / 3 else "Center"
            )
            zone = f"{vertical}-{horizontal}"
            if zone not in zones:
                zones.append(zone)
            boxes.append([
                max(0, int(r) - 1), max(0, int(c) - 1),
                min(self.grid_size, int(r) + 2), min(self.grid_size, int(c) + 2)
            ])
        count = int(len(indices))
        return {
            "anomaly_detected": count > 0,
            "hotspot_count": count,
            "hotspot_zones": zones,
            "bounding_boxes": boxes,
            # A heuristic indicator, not trained-model accuracy.
            "cv_confidence": min(1.0, count / max(1, self.grid_size)),
        }


def generate_telemetry(scenario="normal", seed=None, machine_id="Unit-01",
                       machine_type="Chiller"):
    """Compatibility wrapper used by Member 1's main.py."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    simulator = MachineSimulator(machine_id=machine_id, machine_type=machine_type)
    return simulator.step(scenario=scenario)


def generate_machine_telemetry(machine_id="Machine-01"):
    """Backward-compatible helper retained from Member 2's original file."""
    return generate_telemetry(machine_id=machine_id)
