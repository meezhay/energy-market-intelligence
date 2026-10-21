# Mini-grid market screening: interactive sensitivity analysis
# Run from the repo root with:  streamlit run app.py

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

from src.scoring import calculate_opportunity_scores

st.set_page_config(page_title="Mini-grid market screening", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "processed" / "ssa_market_readiness_v4.csv"


# Slider labels for each score component
WEIGHT_LABELS = {
    "Access_Score": "Access deficit",
    "Population_Score": "People without electricity",
    "GDP_Score": "GDP per capita",
    "Improvement_Score": "Access improvement (2014–2023)",
}

# Each version's weights (0–100, normalised later) and scope threshold
# v1 and v2 had no scope rule, so they use 100% (all countries included)
PRESETS = {
    "v4 (current)": {"Access_Score": 33, "Population_Score": 33, "GDP_Score": 33, "Improvement_Score": 0, "max_access": 90},
    "v2": {"Access_Score": 25, "Population_Score": 25, "GDP_Score": 25, "Improvement_Score": 25, "max_access": 100},
    "v1": {"Access_Score": 33, "Population_Score": 33, "GDP_Score": 0, "Improvement_Score": 33, "max_access": 100},
}


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def apply_preset():
    # Copy the chosen preset's values into the sliders
    preset = PRESETS[st.session_state.preset]
    for key, value in preset.items():
        st.session_state[key] = value


# First run: start from the v4 preset
if "preset" not in st.session_state:
    st.session_state.preset = "v4 (current)"
    apply_preset()

df = load_data()

# ---------- Sidebar controls ----------
st.sidebar.header("Model settings")
st.sidebar.radio("Start from a version", list(PRESETS), key="preset", on_change=apply_preset)
st.sidebar.caption("v3 tested extra indicators and rejected them, so it has no preset.")

st.sidebar.subheader("Weights")
for key, label in WEIGHT_LABELS.items():
    st.sidebar.slider(label, 0, 100, key=key)

st.sidebar.subheader("Scope")
st.sidebar.slider("Exclude countries with 2023 access above (%)", 50, 100, key="max_access")

strict_tariff = st.sidebar.toggle("Treat tariff caps as a hard gate (ignore subsidy route)")

# ---------- Calculate ----------
raw_weights = {key: st.session_state[key] for key in WEIGHT_LABELS}
total = sum(raw_weights.values())
if total == 0:
    st.warning("Set at least one weight above zero.")
    st.stop()

weights = {key: value / total for key, value in raw_weights.items()}

scores = calculate_opportunity_scores(df, weights, max_access=st.session_state.max_access)

result = df.drop(columns=["Opportunity_Score", "Opportunity_Rank", "Score_Status"]).merge(
    scores, on="Country Code", how="left"
)

# Explain every blank score, as in the v4 notebook
result["Score_Status"] = np.select(
    [result["2023"] > st.session_state.max_access, result["Opportunity_Score"].isna()],
    [f"Out of scope (>{st.session_state.max_access}% access)", "Not scored (missing data)"],
    default="Scored",
)

if strict_tariff:
    result["Feasibility"] = result["Feasibility"].replace("Feasible with subsidy support", "Fails a gate")


# v4 baseline ranking, used to show how far each country moves
v4 = PRESETS["v4 (current)"]
v4_weights = {k: v4[k] / sum(v4[k] for k in WEIGHT_LABELS) for k in WEIGHT_LABELS}
baseline = calculate_opportunity_scores(df, v4_weights, max_access=v4["max_access"])

result = result.merge(
    baseline[["Country Code", "Opportunity_Rank"]].rename(columns={"Opportunity_Rank": "Baseline_Rank"}),
    on="Country Code",
    how="left",
)

# Positive = moved up compared with v4; blank if not ranked in one of the two
result["Rank_Change"] = result["Baseline_Rank"] - result["Opportunity_Rank"]


# ---------- Display ----------
st.title("Where should mini-grids go next?")
st.caption(
    "Screening 48 Sub-Saharan African markets. Weights are assumptions: "
    "change them to see how the ranking responds."
)

st.write("**Weights in use:** " + ", ".join(f"{WEIGHT_LABELS[k]} {v:.0%}" for k, v in weights.items() if v > 0))

# Feasibility colours, matching the Power BI dashboard
feasibility_colors = alt.Scale(
    domain=["Currently feasible", "Feasible with subsidy support", "Fails a gate"],
    range=["#2E9E5B", "#E39B2D", "#D9534F"],
)

left, right = st.columns(2)

# Top 10 by opportunity score
with left:
    st.subheader("Top 10 opportunity markets")
    top10 = result.nsmallest(10, "Opportunity_Rank")
    bars = alt.Chart(top10).mark_bar(color="#0F8B7E").encode(
        x=alt.X("Opportunity_Score:Q", title="Opportunity score"),
        y=alt.Y("Country Name:N", sort="-x", title=None),
        tooltip=["Country Name", alt.Tooltip("Opportunity_Score:Q", format=".2f"), "Feasibility"],
    )
    st.altair_chart(bars, use_container_width=True)

# Opportunity vs readiness, only countries with both values
with right:
    st.subheader("Opportunity vs regulatory readiness")
    both = result.dropna(subset=["Opportunity_Score", "RISE_Minigrid_Score"])

    points = alt.Chart(both).mark_circle(size=90).encode(
        x=alt.X("Opportunity_Score:Q", title="Opportunity score"),
        y=alt.Y("RISE_Minigrid_Score:Q", title="RISE mini-grid score (0–100)"),
        color=alt.Color("Feasibility:N", scale=feasibility_colors, legend=alt.Legend(orient="bottom", columns=3, labelLimit=0, title=None)),
        tooltip=["Country Name", alt.Tooltip("Opportunity_Score:Q", format=".2f"),
                 alt.Tooltip("RISE_Minigrid_Score:Q", format=".0f"), "Feasibility", "Failed_Gates"],
    )

    # Average lines split the chart into quadrants, as in the dashboard
    avg_x = alt.Chart(both).mark_rule(strokeDash=[4, 4], color="#14304A").encode(x="mean(Opportunity_Score):Q")
    avg_y = alt.Chart(both).mark_rule(strokeDash=[4, 4], color="#14304A").encode(y="mean(RISE_Minigrid_Score):Q")

    st.altair_chart(points + avg_x + avg_y, use_container_width=True)
    st.caption(f"{len(both)} countries with both an opportunity score and RISE data. Dashed lines show averages.")

table = result.sort_values("Opportunity_Score", ascending=False)[
    ["Country Name", "Opportunity_Rank", "Rank_Change", "Opportunity_Score", "Feasibility",
     "Failed_Gates", "RISE_Minigrid_Score", "2023", "Score_Status"]
]

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Country Name": "Country",
        "Opportunity_Rank": st.column_config.NumberColumn("Rank", format="%d"),
        "Rank_Change": st.column_config.NumberColumn("Change vs v4", format="%+d"),
        "Opportunity_Score": st.column_config.NumberColumn("Opportunity score", format="%.2f"),
        "Failed_Gates": "Failed gates",
        "RISE_Minigrid_Score": st.column_config.NumberColumn("RISE score", format="%.0f"),
        "2023": st.column_config.NumberColumn("Access 2023 (%)", format="%.1f"),
        "Score_Status": "Score status",
    },
)