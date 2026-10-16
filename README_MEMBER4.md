
# EnergyTwinAI: Gemini AI Optimization
## Member 4 Deliverable

### 1. Overview
The AI Optimizer uses Google's Gemini API to analyze machine telemetry and Digital Twin metrics. It generates structured recommendations intended to help reduce energy waste.

### 2. Technologies
- Python
- Google Gemini API
- google-genai
- python-dotenv
- JSON

### 3. Main Function
`get_ai_suggestions(data_dict)`

Accepts a dictionary containing machine telemetry and available Digital Twin metrics. Returns a structured recommendation dictionary.

### 4. Recommendation Output
The output includes:
- machine_id
- provider
- status
- action
- recommended_power_reduction_pct
- summary
- reason
- confidence
- requires_validation

### 5. Validation and Reliability
- Checks recommendation fields and allowed actions.
- Limits suggested reductions to 0–15%.
- Rejects invalid or non-finite reduction values.
- Uses a clearly labeled fallback if Gemini is unavailable.
- Does not treat suggested savings as verified results.

### 6. Configuration
Store the Gemini API key in a local `.env` file.
Never commit `.env` or expose the API key publicly.

### 7. Testing
Run unit tests:
`python -m unittest -v test_ai_optimizer.py`

Test Gemini connectivity:
`python test_gemini.py`

Test the optimizer interface:
`python test_optimizer_interface.py`

### 8. Integration
The module is intended to receive telemetry and Digital Twin metrics from the other project modules. Final integration testing requires the team's actual simulator, Digital Twin, and application files.

### 9. Limitation
Gemini recommendations are advisory. Energy and carbon savings must be calculated by the Digital Twin and verified through simulation.
