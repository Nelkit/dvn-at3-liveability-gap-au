"""
app.py
------
Entry point for the Liveability Gap Streamlit application.

Run with:
    streamlit run app.py

Narrative arc — The Detective:
  "The Story" → Sets the scene; the anomaly is hinted
  "Explore the Data" → Five progressive charts reveal the culprit
  "What If?" → Policy levers for Ministry of Housing
  "About" → Project context and team

Data source:
  All pages use load_data() from src/data_loader.py.
  No raw data is hardcoded in this file.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Local modules — src/ is a sibling of app.py so Python resolves the import
from src.data_loader import load_data
from src.charts import (
    scatter_crime_scene,
    bar_liveability_gap,
    line_price_trends,
    bar_transport_modes,
    map_liveability,
)

# Page configuration — must be the FIRST Streamlit call in the script
st.set_page_config(
    page_title="The Liveability Gap",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS (path is resolved relative to this file for portability)
css_path = Path(__file__).parent / "assets" / "style.css"
try:
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
except Exception:
    pass   # CSS is cosmetic — silently skip if missing so the app still runs

# Data initialisation — load once and cache in session_state
# The cache key includes a schema version string so that any change to
# load_data() that adds or renames columns automatically invalidates
# the cached DataFrame on the next Streamlit reload, preventing stale-schema
# KeyErrors. Bump _SCHEMA_VERSION whenever load_data() output changes.
_SCHEMA_VERSION = "v2"
_CACHE_KEY = f"df_{_SCHEMA_VERSION}"

if _CACHE_KEY not in st.session_state:
    st.session_state[_CACHE_KEY] = load_data()

df: pd.DataFrame = st.session_state[_CACHE_KEY]   # shorthand used throughout


# Sidebar — navigation and global year filter
with st.sidebar:
    st.title("🏙️ The Liveability Gap")
    st.caption(
        "Housing Affordability vs Transport Access · Australian Capital Cities"
    )
    st.divider()

    page = st.radio(
        "Navigate to",
        options=["The Story", "Explore the Data", "What If?", "About"],
        index=0,
        key="nav_page",
    )
    st.divider()

    # Global year slider for data pages (hidden on About)
    # Range is derived from the dataset so no hardcoded years exist here.
    year_min = int(df["year"].min()) if not df.empty else 2002
    year_max = int(df["year"].max()) if not df.empty else 2023

    selected_year: int = st.slider(
        "Reference Year",
        min_value=year_min,
        max_value=year_max,
        value=year_max,
        step=1,
        help="Filters all snapshot charts to the selected financial year start",
    )

    st.divider()
    st.caption("Data: ABS Cat. 6416.0 & BITRE Yearbook 2024")
    st.caption("UTS Master of Data Science · DVN AT3 · 2026")


# PAGE 1 — The Story

def page_the_story() -> None:
    """
    Narrative hook — The Detective opens the case.

    Sets the scene for Real Estate Agent Sarah and Ministry of Housing
    stakeholders.  Introduces the anomaly before any chart is shown so the
    audience arrives at the data with a question already in mind.
    """
    st.markdown(
        "<h1 style='color:#E63946;'>The Liveability Gap</h1>",
        unsafe_allow_html=True,
    )
    st.subheader(
        "Housing Affordability vs Transport Access in Australian Capital Cities"
    )
    st.divider()

    # Opening quote — plants the anomaly in the audience's mind
    st.markdown(
        """
        <div class="callout">
        "Imagine paying $1.8 million for a house in Sydney and still spending
        two hours a day commuting because public transport doesn't reach your suburb."
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Narrative context — the problem and who it affects
    st.markdown("""
    Australia's capital cities face a growing tension between two pillars of
    urban liveability: **housing affordability** and **transport access**.
    Median dwelling prices have surged across every capital city since 2002,
    yet investment in public transport has not kept pace, leaving many
    households priced into locations poorly served by transit.

    This data narrative examines that gap, city by city, year by year,
    and asks: *where is the liveability crisis most acute, and what policy
    levers could close the gap?*
    """)

    # Detective arc framing — tells the audience how to read what follows
    st.markdown("""
    > This is a story about an anomaly. The cities charging the most are not
    > always the ones investing the most in getting residents around.
    > That gap (between what buyers pay and what they get) is what a real
    > estate agent cannot see from price data alone.
    """)

    st.divider()

    # KPI cards — quick orientation snapshot for the selected year
    st.subheader(f"At a Glance: FY {selected_year}–{str(selected_year + 1)[-2:]}")

    # Guard: if df is empty (file missing) the metrics section is skipped gracefully
    if df.empty:
        st.warning(
            "Dataset not loaded. Run `notebooks/data_cleaning.ipynb` to generate "
            "`data/processed/liveability_gap_cleaned.csv`, then restart the app."
        )
        return

    # Slice the full DataFrame to the selected year for all KPI calculations
    yr = df[df["year"] == selected_year]

    if yr.empty:
        st.info(f"No data available for FY {selected_year}. Try a different year.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Most expensive city: central to the liveability story
        row = yr.loc[yr["median_house_price"].idxmax()]
        st.metric(
            label="Most Expensive City",
            value=row["city"],
            delta=f"${row['median_house_price']:,.0f}",
        )

    with col2:
        # Best public transport per capita: the variable buyers overlook
        row = yr.loc[yr["pkm_public_transport_per_capita"].idxmax()]
        st.metric(
            label="Best Transport Access",
            value=row["city"],
            delta=f"{row['pkm_public_transport_per_capita']:,.0f} km/capita",
        )

    with col3:
        # Most affordable city: the contrast to most expensive
        row = yr.loc[yr["median_house_price"].idxmin()]
        st.metric(
            label="Most Affordable City",
            value=row["city"],
            delta=f"${row['median_house_price']:,.0f}",
        )

    with col4:
        # Worst liveability gap: the city the Detective is hunting for (mark inverse to show red = bad)
        row = yr.loc[yr["liveability_gap_index"].idxmax()]
        st.metric(
            label="Worst Liveability Gap",
            value=row["city"],
            delta=f"Index: {row['liveability_gap_index']:.2f}",
            delta_color="inverse",   # inverse: higher index = red = bad
        )

    st.divider()

    # How to read this report
    with st.expander("📖 How to read this report"):
        st.markdown("""
        **Navigate using the sidebar** to move between sections:

        | Section | What you will find |
        |---|---|
        | **The Story** | Narrative context, the research question, and key metrics |
        | **Explore the Data** | Five progressive charts: from the anomaly to the verdict |
        | **What If?** | Policy simulation: model the effect of Ministry interventions |
        | **About** | Project context and team information |

        All snapshot charts respond to the **Reference Year** slider in the sidebar.
        Hover over any data point for exact values.

        **The Detective Arc:**
        Each chart in "Explore the Data" adds one layer of evidence.
        By the end, the culprit (the city most in need of transport investment)
        will be identified by the data itself.
        """)


# PAGE 2 — Explore the Data

def page_explore_data() -> None:
    """
    Five progressive visualisations following the Detective narrative arc.

    Each section adds one layer of evidence, building toward the verdict:
    cities with the worst liveability gap need urgent transport investment.
    """
    st.header("Explore the Data")
    st.caption(
        "Use the Reference Year slider in the sidebar to change the snapshot year."
    )

    if df.empty:
        st.warning("Dataset not loaded. See 'The Story' page for instructions.")
        return

    # Section 1: The Crime Scene (Chart 1, fully connected to real data)
    st.subheader("Act 1 — The Crime Scene")

    # The anomaly callout: Canberra is the real outlier in the data
    st.error(
        "🔍 **The Anomaly:** Canberra is Australia's second most expensive city "
        "yet its residents travel less by public transport per capita than Perth or Adelaide, "
        "cities with significantly lower house prices. "
        "This is the gap a real estate agent cannot explain with price data alone."
    )

    fig_scatter = scatter_crime_scene(df, year=selected_year)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Caption reinforces the quadrant logic after audience sees chart
    st.caption(
        "Cities in the **top-left quadrant** pay the most and get the least in return. "
        "Use the Reference Year slider to track how this anomaly has evolved since 2002."
    )

    st.divider()

    # Section 2: The Verdict (Chart 2, TODO stub)
    st.subheader("Act 2 — The Verdict So Far")

    fig_gap = bar_liveability_gap(df, year=selected_year)
    # Only render if the chart returns a non-empty figure
    if fig_gap.data:
        st.plotly_chart(fig_gap, use_container_width=True)
    else:
        st.info("🚧 Chart coming soon — assigned to team member.")

    st.caption(
        "A higher gap index means residents pay more and travel less by public transport."
    )

    st.divider()

    # Section 3: The Evidence (Chart 3, TODO stub)
    st.subheader("Act 3 — The Evidence: Price Trajectory")

    fig_trends = line_price_trends(df, price_col="median_house_price")
    if fig_trends.data:
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("🚧 Chart coming soon — assigned to team member.")

    st.caption(
        "Track how each city's price trajectory has diverged since 2002."
    )

    st.divider()

    # Section 4: The Clues (Chart 4, TODO stub)
    st.subheader("Act 4 — The Clues: How Each City Moves")

    fig_modes = bar_transport_modes(df, year=selected_year)
    if fig_modes.data:
        st.plotly_chart(fig_modes, use_container_width=True)
    else:
        st.info("🚧 Chart coming soon — assigned to team member.")

    st.caption(
        "The dominant transport mode reveals structural differences in urban "
        "planning across cities."
    )

    st.divider()

    # Section 5: Geographic Overview (Chart 5)
    st.subheader("Act 5 — Where Is the Gap Widest?")

    fig_map = map_liveability(df, year=selected_year)
    if fig_map.data:
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("🚧 Chart coming soon — assigned to team member.")

    st.caption(
        "Larger bubbles = more public transport per person; warmer colours = higher gap index. "
        "Hover each capital for numbers."
    )


# PAGE 3 — What If?

def page_what_if() -> None:
    """
    Policy simulation page for Ministry of Housing and Urban Development.

    Applies illustrative intervention multipliers to real baseline values
    from the cleaned dataset.  No data is hardcoded — baselines come from
    the DataFrame filtered to the selected city and year.
    """
    st.header("What If?")

    # Stakeholder framing — connects to the Ministry of Housing hat
    st.markdown(
        "Model how targeted interventions by the **Ministry of Housing and "
        "Urban Development** could shift the liveability balance for buyers "
        "in each city."
    )

    st.info(
        "🚧 **Illustrative model**: Projections use simplified multipliers. "
        "A production model requires peer-reviewed elasticity estimates.",
        icon="🔧",
    )

    if df.empty:
        st.warning("Dataset not loaded. See 'The Story' page for instructions.")
        return

    st.divider()

    # Intervention controls
    st.subheader("Intervention Levers")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("**Housing Supply Shock**")
        supply_increase = st.slider(
            "Increase in new dwelling approvals (%)",
            min_value=0, max_value=100, value=20, step=5,
            help="Simulates a government-led increase in housing supply",
        )
        stamp_duty_cut = st.slider(
            "Stamp duty reduction (%)",
            min_value=0, max_value=100, value=50, step=10,
            help="Models the price impact of reducing stamp duty",
        )

    with col2:
        st.markdown("**Transport Investment**")
        # City selector is derived from the dataset — no hardcoded list
        available_cities = sorted(df["city"].unique().tolist())
        selected_city = st.selectbox(
            "Target city", options=available_cities, index=0
        )
        transport_investment = st.slider(
            "Additional annual transport investment ($B)",
            min_value=0.0, max_value=10.0, value=1.0, step=0.5,
            help="Simulates increased public transport funding",
        )
        new_lines = st.number_input(
            "New rail/BRT corridors", min_value=0, max_value=10, value=1, step=1
        )

    st.divider()

    # Projected outcome: real baselines, illustrative multipliers
    st.subheader(f"Projected Outcome — {selected_city}")

    # Pull real baseline values for the chosen city and year
    baseline = df[
        (df["city"] == selected_city) & (df["year"] == selected_year)
    ]

    if baseline.empty:
        st.info(
            f"No data for {selected_city} in FY {selected_year}. "
            "Try a different year or city."
        )
        return

    base_price     = baseline["median_house_price"].values[0]
    base_transport = baseline["pkm_public_transport_per_capita"].values[0]

    # Illustrative elasticity model: supply shock reduces price by ~8% per 100%
    # increase in approvals; transport investment lifts per-capita km by ~15% per $5B.
    simulated_price_reduction  = base_price     * (supply_increase  / 100) * 0.08
    simulated_transport_uplift = base_transport * (transport_investment / 5) * 0.15

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            label="Estimated Price Reduction",
            value=f"${simulated_price_reduction:,.0f}",
            delta=f"-{simulated_price_reduction / base_price * 100:.1f}%",
            delta_color="inverse",   # inverse: price reduction is good → green
        )
    with c2:
        st.metric(
            label="Estimated Transport Uplift",
            value=f"+{simulated_transport_uplift:,.0f} km/capita",
            delta=f"+{simulated_transport_uplift / base_transport * 100:.1f}%",
        )

    st.caption(
        "⚠️ These projections use simplified illustrative multipliers. "
        "A proper model requires elasticity estimates from peer-reviewed literature."
    )


# PAGE 4 — About

def page_about() -> None:
    """
    About page — project context and team information.
    """
    st.header("About This Project")
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Research Context

        This analysis investigates the growing tension between **housing affordability**
        and **transport access** in Australian capital cities. We examine how median
        dwelling prices and public transport investment have diverged since 2002,
        and identify which cities face the most acute liveability crisis.

        ### Academic Submission

        - **Course**: ANLP 36118 — Data Visualisation & Narrative
        - **University**: University of Technology Sydney, Master of Data Science
        - **Deadline**: May 4, 2026

        ### Data Sources

        - **Housing Prices**: ABS Catalogue 6416.0 — Residential Property Price
        - **Transport**: BITRE Yearbook 2024 — Passenger km by mode and city
        - **Geographic Data**: Australian Bureau of Statistics, SA4-level classifications
        """)

    with col2:
        st.markdown("""
        ### Team

        - Nelkit Chavez
        - Saurabh Sabharwal
        - Nipun Mudgal
        - Raunak Dhirajkumar Singh
        - Shriram Gajanan Kulkarni
        - Sheshan Munusamy Neelavathi
        - Masaki

        ### Narrative Design

        This app follows a **Detective narrative arc**:

        1. **The Story** — Scene-setting and the core anomaly
        2. **Explore the Data** — Five progressive evidence charts
        3. **What If?** — Policy simulation for Ministry decision-makers
        4. **About** — Project context and team information
        """)

    st.divider()
    st.caption(
        "Built with Streamlit • Data processed with Python (pandas, plotly) • "
        "Academic integrity: all methods documented in companion notebooks."
    )


# Router: render the selected page

if page == "The Story":
    page_the_story()
elif page == "Explore the Data":
    page_explore_data()
elif page == "What If?":
    page_what_if()
elif page == "About":
    page_about()
