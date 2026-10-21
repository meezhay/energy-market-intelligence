# Mini-grid market screening: interactive sensitivity analysis
# Run from the repo root with:  python -m streamlit run app.py

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.scoring import calculate_opportunity_scores

st.set_page_config(page_title="Mini-grid market screening", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "processed" / "ssa_market_readiness_v4.csv"

# Slider label and hover explanation for each score component
WEIGHT_INFO = {
        "Access_Score": (
        "Access deficit",
        "Electricity access percentage deficit: countries with lower 2023 access score higher.",
    ),
    "Population_Score": (
        "People without electricity",
        "Number of people without electricity: countries with more people lacking access score higher.",
    ),
    "GDP_Score": (
        "GDP per capita",
        "Economic capacity: countries with higher GDP per capita (log scale) score higher.",
    ),
    "Improvement_Score": (
        "Access improvement (2014–2023)",
        "Change in electricity access from 2014 to 2023: faster gains score higher. Set to 0 by default, as fast progress can signal an active market or a shrinking one.",
    ),
}

# v4 baseline: equal importance for access, population, GDP; improvement excluded
DEFAULTS = {"Access_Score": 33, "Population_Score": 33, "GDP_Score": 33, "Improvement_Score": 0, "max_access": 90}


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def reset_to_v4():
    # Put every control back to the v4 baseline
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def normalise(raw):
    # Turn importance values (0–10) into weights that sum to 1
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


# First run: start from the v4 baseline
if "max_access" not in st.session_state:
    reset_to_v4()

df = load_data()

# ---------- Sidebar controls ----------
st.sidebar.header("Model settings")
st.sidebar.button("Reset to baseline", on_click=reset_to_v4)

st.sidebar.subheader("Importance of each factor")
st.sidebar.caption("Move the sliders to set how much each factor matters. The share under each slider is its actual weight in the score; the shares always add up to 100%.")

raw_now = {key: st.session_state[key] for key in WEIGHT_INFO}
total_now = sum(raw_now.values())

for key, (label, explanation) in WEIGHT_INFO.items():
    st.sidebar.slider(label, 0, 100, key=key, help=explanation)
    share = raw_now[key] / total_now if total_now else 0
    st.sidebar.caption(f"= {share:.0%} of the score")

strict_tariff = st.sidebar.toggle(
    "Treat tariff caps as a hard gate",
    help="When on, countries that cap tariffs but fund the revenue gap through subsidy are counted as failing a gate.",
)

# ---------- Calculate ----------
raw_weights = {key: st.session_state[key] for key in WEIGHT_INFO}
if sum(raw_weights.values()) == 0:
    st.warning("Set at least one factor above zero.")
    st.stop()

weights = normalise(raw_weights)

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
baseline_weights = normalise({key: DEFAULTS[key] for key in WEIGHT_INFO})
baseline = calculate_opportunity_scores(df, baseline_weights, max_access=DEFAULTS["max_access"])

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

weights_text = ", ".join(
    f"{WEIGHT_INFO[k][0]} {v:.0%}" for k, v in weights.items() if v > 0
)
st.write(f"**Weights in use:** {weights_text}")

# Feasibility colours, matching the Power BI dashboard
feasibility_colors = alt.Scale(
    domain=["Currently feasible", "Feasible with subsidy support", "Fails a gate"],
    range=["#2E9E5B", "#E39B2D", "#D9534F"],
)

left, right = st.columns(2)

# Top 10 by opportunity score
with left:
    st.subheader(
        "Top 10 opportunity markets",
        help="The ten highest opportunity scores under the weights you have set.",
    )
    top10 = result.nsmallest(10, "Opportunity_Rank")
    bars = alt.Chart(top10).mark_bar(color="#0F8B7E").encode(
        x=alt.X("Opportunity_Score:Q", title="Opportunity score"),
        y=alt.Y("Country Name:N", sort="-x", title=None),
        tooltip=["Country Name", alt.Tooltip("Opportunity_Score:Q", format=".2f"), "Feasibility"],
    )
    st.altair_chart(bars, use_container_width=True)

# Opportunity vs readiness, only countries with both values
with right:
    st.subheader(
        "Opportunity vs regulatory readiness",
        help=(
            "Each dot is a country. Further right means a larger market opportunity; higher up means "
            "stronger mini-grid regulation (RISE 2023). Top-right countries combine both. "
            "Colour shows whether the regulatory gates are met."
        ),
    )
    both = result.dropna(subset=["Opportunity_Score", "RISE_Minigrid_Score"])

    points = alt.Chart(both).mark_circle(size=90).encode(
        x=alt.X("Opportunity_Score:Q", title="Opportunity score"),
        y=alt.Y("RISE_Minigrid_Score:Q", title="RISE mini-grid score (0–100)"),
        color=alt.Color(
            "Feasibility:N",
            scale=feasibility_colors,
            legend=alt.Legend(orient="bottom", columns=3, labelLimit=0, title=None),
        ),
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

# Download: the ranking plus the settings that produced it, so results stay reproducible
settings_header = (
    f"# Weights: {weights_text}\n"
    f"# Scope: countries with 2023 access above {st.session_state.max_access}% excluded\n"
    f"# Tariff caps treated as a hard gate: {'yes' if strict_tariff else 'no'}\n"
)
st.download_button(
    "Download this ranking (CSV)",
    data=settings_header + table.to_csv(index=False),
    file_name="minigrid_ranking.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "Data: World Bank, World Development Indicators (2023); World Bank/ESMAP, "
    "Regulatory Indicators for Sustainable Energy (RISE), 2023. "
    "A screening tool for further investigation, not investment advice. "
    "Code and methodology: github.com/meezhay/energy-market-intelligence"
)