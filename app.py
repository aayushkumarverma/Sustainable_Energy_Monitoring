"""EcoTwin AI | Industrial-grade Streamlit demonstration dashboard.

Works with the existing run_simulation(...) contract in main.py.
No changes to simulator.py / digital_twin.py / ai_optimizer.py required.
"""

import html
import json
from datetime import datetime, timezone

import plotly.graph_objects as go
import streamlit as st


st.markdown("""
<style>
/* Make the Streamlit top header dark */
[data-testid="stHeader"] {
    background-color: #0b1220;
}

/* Match the main dashboard background */
[data-testid="stAppViewContainer"] {
    background-color: #0b1220;
}

/* Remove extra top spacing above the dashboard */
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


from main import run_simulation


# ─── App configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoTwin AI | Industrial Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B1220"
PANEL = "#111D30"
GRID = "#27354A"
MUTED = "#91A5C0"
WHITE = "#E8EFF8"
TEAL = "#32D7B3"
BLUE = "#6AA9FF"
AMBER = "#FFBC66"
RED = "#FF7D84"

st.markdown(
    """
<style>
  :root { color-scheme: dark; }
  .stApp { background: #0B1220; color: #E8EFF8; }
  [data-testid="stSidebar"] {
    background: #0E192B;
    border-right: 1px solid #233248;
  }
  [data-testid="stSidebar"] .stMarkdown { color: #E8EFF8; }
  
  /* Give the dashboard enough space at the top */
  .block-container {
      padding-top: 2.5rem !important;
      padding-bottom: 1rem;
  }

  /* Keep the Streamlit header from covering content */
  [data-testid="stHeader"] {
      background-color: #0b1220;
      height: 0rem;
  }

  /* Prevent the main content from shifting upward */
  [data-testid="stAppViewContainer"] .main .block-container {
      margin-top: 0.5rem;
  }

  [data-testid="stMetricLabel"] { color: #A1B1C7; }
  [data-testid="stMetricValue"] { color: #EFF7FF; font-weight: 750; }
  [data-testid="stMetricDelta"] { color: #32D7B3; }
  div.stButton > button[kind="primary"] {
    background: #22BDA0;
    color: #06161A;
    border: 0;
    border-radius: 10px;
    font-weight: 750;
    min-height: 47px;
  }
  div.stButton > button[kind="primary"]:hover {
    background: #45E2C2; color: #06161A;
  }
  [data-testid="stTabs"] button { color: #A5B5CB; font-weight: 650; }
  [data-testid="stTabs"] button[aria-selected="true"] { color: #32D7B3; }
  [data-testid="stPlotlyChart"] {
    border: 1px solid #25364D;
    border-radius: 15px;
    overflow: hidden;
    background: #111D30;
  }
  [data-testid="stExpander"] {
    background: #111D30; border: 1px solid #25364D; border-radius: 12px;
  }
  .ec-title-row {display:flex; align-items:center; gap: 13px; margin-bottom: 5px;}
  .ec-logo {
    display:grid; place-items:center; width:48px; height:48px;
    background: linear-gradient(140deg, #1B7C82, #16655B);
    border:1px solid #36DAB4; border-radius:14px;
    color:#E7FFF9; font-size:25px;
    box-shadow: 0 0 25px #32D7B320;
  }
  .ec-title { font-size: 2.0rem; line-height:1.12; font-weight:800; letter-spacing:-.05em; color:#F4F8FF; }
  .ec-sub { color:#A9BDD3; margin-bottom: 12px; font-size:.94rem; }
  .ec-eyebrow { color:#32D7B3; font-size:.73rem; font-weight:750;
                letter-spacing:.16em; text-transform:uppercase; }
  .ec-chip { display:inline-flex; align-items:center; gap:7px; padding:7px 12px;
             border-radius:50px; font-size:.78rem; font-weight:750;
             background:#203146; border:1px solid #344660; color:#C3D4EA; }
  .ec-status {
    padding:14px 18px; border-radius:12px; margin:17px 0 21px;
    background:#102D2D; border:1px solid #277A68; color:#BCFCE9;
  }
  .ec-status.danger { background:#35202A; border-color:#87434D; color:#FFCBCE; }
  .ec-status strong { font-weight:800; }
  .ec-section { font-size:1.03rem; font-weight:750; color:#F0F5FC; margin:13px 0 9px; }
  .ec-info {
    border:1px solid #273B55; border-radius:14px; padding:17px 19px;
    background:linear-gradient(135deg, #12233A, #101B2E); margin-bottom:12px;
  }
  .ec-label { color:#94A9C4; font-size:.77rem; text-transform:uppercase;
              font-weight:750; letter-spacing:.1em; margin-bottom:9px; }
  .ec-value { color:#EAF4FF; font-size:1.05rem; font-weight:700; line-height:1.5; }
  .ec-detail { color:#B1C4D8; font-size:.87rem; line-height:1.6; }
  .ec-action { color:#E8FFF8; font-size:1.18rem; font-weight:730; line-height:1.45; }
  .ec-kicker { font-size:.76rem; font-weight:700; letter-spacing:.11em; color:#71D9C4; }
  .ec-sidebar-brand { font-size:1.3rem; font-weight:800; color:#F4F8FF; margin-bottom:3px; }
  .ec-footer {font-size:.80rem; color:#8094AE; border-top:1px solid #25364D;
              padding-top:16px; margin-top:20px; line-height:1.7;}
  @media (max-width: 800px) { .ec-title {font-size:1.5rem;} }
</style>
""",
    unsafe_allow_html=True,
)


def safe(value):
    """Escape external text before inserting it in HTML cards."""
    return html.escape(str(value), quote=True)


def panel(label, value, detail=""):
    """Visual-only panel. All externally sourced values are escaped."""
    st.markdown(
        '<div class="ec-info">'
        f'<div class="ec-label">{safe(label)}</div>'
        f'<div class="ec-value">{safe(value)}</div>'
        + (f'<div class="ec-detail">{safe(detail)}</div>' if detail else '')
        + '</div>',
        unsafe_allow_html=True,
    )


def style_plot(fig, height=320):
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=WHITE, family="Segoe UI, Arial, sans-serif", size=12),
        margin=dict(t=40, r=28, b=35, l=45),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        hoverlabel=dict(bgcolor="#1D2A3F"),
    )
    return fig


def comparison_chart(title, before, after, unit, accent=TEAL):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Baseline", "Projected"],
            y=[before, after],
            marker_color=["#527293", accent],
            text=[f"{before:,.2f}", f"{after:,.2f}"],
            textposition="outside",
            textfont=dict(color=WHITE, size=14),
            width=0.48,
            hovertemplate=f"%{{x}}: %{{y:,.2f}} {unit}<extra></extra>",
        )
    )
    style_plot(fig, height=320)
    fig.update_layout(title=dict(text=title, font=dict(size=16)), yaxis_title=unit)
    fig.update_yaxes(range=[0, max(float(before), float(after), 0.1) * 1.25])
    return fig


def thermal_chart(heatmap, height=370):
    fig = go.Figure(
        go.Heatmap(
            z=heatmap,
            colorscale="Inferno",
            zmin=40,
            zmax=100,
            colorbar=dict(title=dict(text="°C", side="top"), thickness=12),
            hovertemplate="Sensor cell (%{x}, %{y})<br>%{z:.1f} °C<extra></extra>",
        )
    )
    style_plot(fig, height=height)
    fig.update_layout(
        margin=dict(t=22, b=20, l=20, r=20),
        xaxis=dict(showticklabels=False, showgrid=False, fixedrange=True),
        yaxis=dict(showticklabels=False, showgrid=False, autorange="reversed", fixedrange=True),
    )
    return fig


# ─── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div class="ec-sidebar-brand">◈ EcoTwin Control</div>'
    '<div style="color:#93A8C0; font-size:.84rem; margin-bottom:18px;">'
    'DIGITAL TWIN • CONTROL DESK</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown("### Simulation setup")
scenario_label = st.sidebar.selectbox(
    "Equipment condition",
    ["Normal operation", "Overheating / hotspot"],
    help="Changes simulated thermal-camera conditions for the single HVAC unit.",
)
selected_scenario = "normal" if scenario_label == "Normal operation" else "overheating"
emission_factor = st.sidebar.number_input(
    "Grid emission factor (kg CO₂e/kWh)",
    min_value=0.0, max_value=2.0, value=0.70, step=0.05,
    help="Assumed factor; not a live grid feed.",
)
electricity_rate = st.sidebar.number_input(
    "Electricity tariff (₹/kWh)",
    min_value=0.0, max_value=50.0, value=8.0, step=0.50,
)
fixed_seed = st.sidebar.checkbox(
    "Repeatable demo readings", value=True,
    help="Use a fixed random seed so judges can compare the same scenario.",
)
run_clicked = st.sidebar.button(
    "⚡ Run Digital Twin", type="primary", use_container_width=True,
)
st.sidebar.divider()
st.sidebar.markdown("**PIPELINE**")
st.sidebar.caption("01  ·  Simulated sensors & thermal image")
st.sidebar.caption("02  ·  Baseline Digital Twin")
st.sidebar.caption("03  ·  Gemini / labeled rule fallback")
st.sidebar.caption("04  ·  Projected savings calculation")
st.sidebar.divider()
st.sidebar.caption("Prototype mode · No physical equipment connected")


# ─── State: run only on initial load or explicit click ───────────────────────
def execute_pipeline(scenario, factor, tariff, seed):
    try:
        output = run_simulation(
            scenario=scenario,
            emission_factor=factor,
            electricity_rate=tariff,
            seed=seed,
        )
        st.session_state["ecotwin_result"] = output
        st.session_state["ecotwin_context"] = {
            "scenario": scenario,
            "emission_factor": factor,
            "electricity_rate": tariff,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        st.session_state.pop("ecotwin_error", None)
    except Exception as exc:
        st.session_state["ecotwin_error"] = f"{type(exc).__name__}: {exc}"


if "ecotwin_result" not in st.session_state:
    with st.spinner("Preparing the initial monitoring snapshot..."):
        execute_pipeline("normal", 0.70, 8.0, 42)
elif run_clicked:
    with st.spinner("Generating telemetry and evaluating the digital twin..."):
        execute_pipeline(
            selected_scenario,
            emission_factor,
            electricity_rate,
            42 if fixed_seed else None,
        )

if "ecotwin_error" in st.session_state:
    st.error("The newest run could not complete: " + st.session_state["ecotwin_error"])
    st.caption("Check module function signatures and input/output field names.")

if "ecotwin_result" not in st.session_state:
    st.stop()

result = st.session_state["ecotwin_result"]
context = st.session_state["ecotwin_context"]
telemetry = result["telemetry"]
before = result["baseline"]
after = result["optimized"]
advice = result["recommendation"]
savings = result["savings"]

anomaly = bool(telemetry.get("cv_anomaly", False))
reduction = float(advice["recommended_power_reduction_pct"])
blocked = anomaly or bool(advice.get("requires_inspection", False))


# ─── Branding / status ──────────────────────────────────────────────────────
st.markdown(
    '<div class="ec-title-row">'
    '<div class="ec-logo">⚡</div>'
    '<div><div class="ec-eyebrow">Industrial intelligence / monitoring console</div>'
    '<div class="ec-title">EcoTwin <span style="color:#32D7B3">AI</span></div></div>'
    '</div>'
    '<div class="ec-sub">Energy optimization & carbon analytics powered by a simulated digital twin</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<span class="ec-chip">◈ SIMULATION MODE</span> '
    f'<span class="ec-chip">Machine: {safe(before["machine_id"])}</span> '
    f'<span class="ec-chip">Snapshot: {safe(context["timestamp_utc"])}</span>',
    unsafe_allow_html=True,
)

if blocked:
    st.markdown(
        '<div class="ec-status danger"><strong>⚠ Thermal risk detected — optimization paused.</strong> '
        'Inspection is recommended before considering energy reduction.</div>',
        unsafe_allow_html=True,
    )
elif reduction <= 0:
    st.markdown(
        '<div class="ec-status"><strong>● Monitoring active.</strong> '
        'No power reduction is recommended for this snapshot.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="ec-status"><strong>● Operating state normal.</strong> '
        'A virtual optimization scenario is ready for review.</div>',
        unsafe_allow_html=True,
    )

# ─── Headline KPIs ──────────────────────────────────────────────────────────
a, b, c, d = st.columns(4)
a.metric("BASELINE ENERGY", f'{before["energy_kwh"]:,.2f} kWh')
b.metric("PEAK TEMPERATURE", f'{before["temperature_c"]:,.1f} °C')
c.metric("PROPOSED REDUCTION", f"{reduction:.1f}%")
d.metric("PROJECTED CO₂e SAVED", f'{savings["carbon_kg"]:,.2f} kg')

# ─── Content tabs ───────────────────────────────────────────────────────────
tab_overview, tab_thermal, tab_ai = st.tabs(
    ["▣   Overview", "▤   Thermal Diagnostics", "✦   AI & Digital Twin"]
)

with tab_overview:
    st.markdown('<div class="ec-section">Baseline vs projected energy impact</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            comparison_chart("Energy consumption", before["energy_kwh"], after["energy_kwh"], "kWh"),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            comparison_chart("Carbon emissions", before["carbon_kg"], after["carbon_kg"], "kg CO₂e", BLUE),
            use_container_width=True,
        )

    x, y, z = st.columns(3)
    with x:
        panel("Projected energy savings", f'{savings["energy_kwh"]:,.2f} kWh', "Same simulated runtime")
    with y:
        panel("Projected electricity savings", f'₹{savings["cost_inr"]:,.2f}', "Uses the selected assumed tariff")
    with z:
        panel("Operational score · demo", f'{before.get("efficiency_score", 0):,.1f} / 100', "Illustrative indicator, not a measured efficiency")
    st.caption("Comparisons are virtual projections based on a constant runtime and proportional reduction in average power.")

with tab_thermal:
    st.markdown('<div class="ec-section">Infrared inspection · simulated thermal sensor matrix</div>', unsafe_allow_html=True)
    left, right = st.columns([1.45, 1])
    with left:
        st.plotly_chart(thermal_chart(telemetry["thermal_heatmap"]), use_container_width=True)
        st.caption("Synthetic 8 × 8 heatmap. Bright cells represent hotter regions of the simulated equipment.")
    with right:
        panel("Equipment", before["machine_id"], "Asset: industrial HVAC demonstration unit")
        panel("Sensor peak", f'{before["temperature_c"]:.2f} °C', "Thermal alert heuristic uses an 82°C pixel threshold")
        panel("CV anomaly", "DETECTED" if anomaly else "NOT DETECTED", "Threshold-driven hotspot inspection")
        panel("Detection signal score", f'{float(telemetry.get("cv_confidence", 0)):.0%}', "Heuristic score; not trained-model accuracy")
    st.markdown('<div class="ec-section">Operational telemetry</div>', unsafe_allow_html=True)
    p, q, r = st.columns(3)
    with p:
        st.metric("Average power", f'{before["power_kw"]:.2f} kW')
    with q:
        st.metric("Runtime", f'{before["runtime_hours"]:.2f} hours')
    with r:
        st.metric("Machine condition", str(before["status"]).upper())

with tab_ai:
    st.markdown('<div class="ec-section">Optimization reasoning & virtual execution</div>', unsafe_allow_html=True)
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown(
            '<div class="ec-info"><div class="ec-label">Recommendation engine</div>'
            f'<div class="ec-value" style="color:#32D7B3">{safe(advice.get("source", "Unknown source"))}</div>'
            '</div>', unsafe_allow_html=True,
        )
        st.markdown('<div class="ec-kicker">RECOMMENDED ACTION</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ec-info"><div class="ec-action">{safe(advice.get("action", "No recommendation"))}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ec-kicker">ENGINEERING RATIONALE</div>', unsafe_allow_html=True)
        st.write(advice.get("reasoning", "Not provided"))
        if advice.get("note"):
            st.caption(advice["note"])
    with right:
        panel("Optimization mode", "SAFETY HOLD" if blocked else "SIMULATION ONLY")
        panel("Power adjustment", f"{reduction:.1f}%", "Applied to average power in the virtual twin")
        panel("Projected power", f'{after["power_kw"]:.2f} kW', f'Baseline: {before["power_kw"]:.2f} kW')
        panel("Cost impact", f'₹{savings["cost_inr"]:,.2f} saved', "Illustrative tariff-based estimate")

    st.markdown('<div class="ec-section">Model assumptions & evidence</div>', unsafe_allow_html=True)
    st.markdown(
        f'- Grid emissions factor: **{before["emission_factor_used"]:.2f} kg CO₂e/kWh** (assumed)\n'
        f'- Electricity price: **₹{before["electricity_rate_used"]:.2f}/kWh** (assumed)\n'
        '- No physical actuation or post-change sensor verification is performed.\n'
        '- Gemini is used only if the recommendation source explicitly says **Google Gemini**.\n'
    )

    payload = {
        "project": "EcoTwin AI",
        "mode": "Simulated digital twin",
        "snapshot": context,
        "data": result,
        "disclaimer": "Projected savings only; no physical verification or machine actuation.",
    }
    st.download_button(
        "↓ Download simulation report (JSON)",
        data=json.dumps(payload, indent=2, default=str, ensure_ascii=False),
        file_name="ecotwin_simulation_report.json",
        mime="application/json",
        use_container_width=True,
    )

with st.expander("Developer view: full structured pipeline output"):
    st.json(result)

st.markdown(
    '<div class="ec-footer">'
    'ECOTWIN AI · HACKATHON PROTOTYPE · SYNTHETIC TELEMETRY<br>'
    'The dashboard displays estimated energy and emissions impacts, not verified real-world reductions. '
    'Operating scores and CV signal scores are illustrative. No industrial equipment is controlled.'
    '</div>',
    unsafe_allow_html=True,
)
