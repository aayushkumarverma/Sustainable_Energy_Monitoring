# EcoTwin AI integration patch

## Files
- `digital_twin.py`: validated energy, carbon, cost, and optimization calculations.
- `simulator.py`: retains `MachineSimulator` and `generate_machine_telemetry()`, and adds `generate_telemetry()` expected by `main.py`.
- `main.py`: orchestration with a thermal-safety hold.

## Apply
Back up the original files first. Copy these files into the same project folder as `app.py` and `ai_optimizer.py`, replacing the matching files only after your team agrees.

Install dependencies from the repository's `requirements.txt`. The simulator and Digital Twin use NumPy; the dashboard also uses Streamlit and Plotly. The `main.py` pipeline requires the repository's `ai_optimizer.py`.

## Assumptions and notes
- One generated telemetry snapshot represents an illustrative 8-hour window. Confirm this assumption with your team and change `runtime_hours` if your demonstration uses a different interval.
- The 8x8 thermal heatmap and 82°C threshold align with the dashboard labels.
- `cv_confidence` is a heuristic signal, not trained-model accuracy.
- Energy savings are projected at constant runtime; no real machine is controlled.
- The full dashboard pipeline cannot be tested without the matching `ai_optimizer.py` file and installed dependencies.
