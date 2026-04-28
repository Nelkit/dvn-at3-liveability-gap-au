"""
app.py
------
Entry point for the Liveability Gap Streamlit application.

Run with:
    streamlit run app.py

Structure:
  - Sidebar navigation selects one of three pages
  - Each page is rendered by a dedicated function below
  - All data is loaded once and stored in st.session_state for efficiency
"""

import streamlit as st

# Local modules — src/ is on the path because it sits next to app.py
from src.data_loader import load_placeholder_data
from src.charts import (
    scatter_price_vs_transport,
    map_liveability,
    line_price_trends,
    bar_transport_modes,
)

# ---------------------------------------------------------------------------
# Page configuration — must be the FIRST Streamlit call in the script
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="The Liveability Gap",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load custom CSS from assets/style.css
# ---------------------------------------------------------------------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data initialisation — load once, cache in session_state
# ---------------------------------------------------------------------------
if "df" not in st.session_state:
    # Replace load_placeholder_data() with real loaders when data is ready
    st.session_state.df = load_placeholder_data()

df = st.session_state.df  # convenient shorthand used throughout


# ---------------------------------------------------------------------------
# Sidebar — navigation and global controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🏙️ The Liveability Gap")
    st.caption("Housing Affordability vs Transport Access · Australian Capital Cities")

    st.divider()

    # Primary page selector
    page = st.radio(
        "Navigate to",
        options=["The Story", "Explore the Data", "What If?"],
        index=0,
        key="nav_page",
    )

    st.divider()

    # Global year filter — affects all charts simultaneously
    selected_year = st.slider(
        "Reference Year",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=int(df["year"].max()),
        step=1,
        help="Select the year shown in snapshot charts",
    )

    st.divider()
    st.caption("Data: ABS Cat. 6416.0 & BITRE Urban Transport Statistics")
    st.caption("UTS Master of Data Science · DVN AT3 · 2025")


# ===========================================================================
# PAGE 1 — The Story
# ===========================================================================

def page_the_story() -> None:
    """Narrative hook: sets the scene and motivates the data exploration."""

    # Hero header
    st.markdown(
        "<h1 style='color:#E63946;'>The Liveability Gap</h1>",
        unsafe_allow_html=True,
    )
    st.subheader("Housing Affordability vs Transport Access in Australian Capital Cities")

    st.divider()

    # --- Narrative hook ---
    st.markdown(
        """
        <div class="callout">
        "Imagine paying $1.8 million for a house in Sydney — and still spending
        two hours a day commuting because public transport doesn't reach your suburb."
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    Australia's capital cities face a growing tension between two pillars of
    urban liveability: **housing affordability** and **transport access**.
    Over the past five years, median dwelling prices have surged across every
    capital city — yet investment in public transport has not kept pace,
    leaving many households priced into locations poorly served by transit.

    This data narrative examines that gap, city by city, year by year —
    and asks: *where is the liveability crisis most acute, and what policy
    levers could close the gap?*
    """)

    st.divider()

    # --- Key metrics row — quick orientation for policy audience ---
    st.subheader("At a Glance — " + str(selected_year))

    latest = df[df["year"] == selected_year]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        most_expensive = latest.loc[latest["median_house_price"].idxmax()]
        st.metric(
            label="Most Expensive City",
            value=most_expensive["city"],
            delta=f"${most_expensive['median_house_price']:,.0f}",
        )
    with col2:
        most_accessible = latest.loc[
            latest["transport_patronage_per_capita"].idxmax()
        ]
        st.metric(
            label="Best Transport Access",
            value=most_accessible["city"],
            delta=f"{most_accessible['transport_patronage_per_capita']:.1f} boardings/capita",
        )
    with col3:
        least_expensive = latest.loc[latest["median_house_price"].idxmin()]
        st.metric(
            label="Most Affordable City",
            value=least_expensive["city"],
            delta=f"${least_expensive['median_house_price']:,.0f}",
        )
    with col4:
        # Liveability gap = price spread between most and least expensive city
        gap = (latest["median_house_price"].max()
               - latest["median_house_price"].min())
        st.metric(
            label="Price Gap (High – Low)",
            value=f"${gap:,.0f}",
            delta="AUD",
        )

    st.divider()

    # --- Narrative arc explanation ---
    with st.expander("📖 How to read this report"):
        st.markdown("""
        **Navigate using the sidebar** to move between three sections:

        | Section | What you will find |
        |---|---|
        | **The Story** | Narrative context, key metrics, and the research question |
        | **Explore the Data** | Interactive charts — scatter, map, trends, transport modes |
        | **What If?** | Policy simulation sliders — model the effect of interventions |

        All charts respond to the **Reference Year** slider in the sidebar.
        Hover over any data point for exact values.
        """)


# ===========================================================================
# PAGE 2 — Explore the Data
# ===========================================================================

def page_explore_data() -> None:
    """Four interactive Plotly visualisations for data exploration."""

    st.header("Explore the Data")
    st.caption(
        "Use the Reference Year slider in the sidebar to change the snapshot year."
    )

    # ---- Row 1: Scatter + Map side by side --------------------------------
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        st.subheader("Price vs Transport Access")
        st.caption(
            "Each bubble is a city. Size = population. "
            "Cities in the top-left quadrant are expensive AND poorly served."
        )
        # Scatter: house price vs boardings per capita for the selected year
        fig_scatter = scatter_price_vs_transport(df, year=selected_year)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_right:
        st.subheader("Geographic Overview")
        st.caption(
            "Bubble size = transport patronage per capita. "
            "Colour = median house price (red = expensive, green = affordable)."
        )
        # Bubble map centred on Australia
        fig_map = map_liveability(df, year=selected_year)
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # ---- Row 2: Line chart (price trends) ---------------------------------
    st.subheader("Dwelling Price Trends — 2020 to 2025")
    st.caption("Toggle between house and unit prices using the selector below.")

    # Let the user switch between house and unit price in the same chart
    price_type = st.radio(
        "Price type",
        options=["median_house_price", "median_unit_price"],
        format_func=lambda x: "Houses" if x == "median_house_price" else "Units / Apartments",
        horizontal=True,
        key="price_type_selector",
    )
    fig_line = line_price_trends(df, price_type=price_type)
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ---- Row 3: Bar chart (transport modes) --------------------------------
    st.subheader("Transport Patronage by Mode and City")
    st.caption(
        "Annual boardings per capita for the selected year. "
        "Colour indicates the dominant transport mode. "
        "Note: placeholder data uses one mode per city — "
        "real BITRE data will show full mode breakdown."
    )
    fig_bar = bar_transport_modes(df, year=selected_year)
    st.plotly_chart(fig_bar, use_container_width=True)


# ===========================================================================
# PAGE 3 — What If?
# ===========================================================================

def page_what_if() -> None:
    """Policy simulation placeholder — sliders modelling hypothetical interventions."""

    st.header("What If?")
    st.markdown(
        "Use these sliders to model how targeted policy interventions could "
        "change the liveability balance across Australian capital cities."
    )

    st.info(
        "🚧 **Coming soon** — This section will include interactive simulations "
        "once the real ABS and BITRE datasets are loaded. "
        "The controls below preview the planned interaction model.",
        icon="🔧",
    )

    st.divider()

    # ---- Placeholder intervention controls --------------------------------
    st.subheader("Intervention Levers")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("**Housing Supply Shock**")
        supply_increase = st.slider(
            "Increase in new dwelling approvals (%)",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="Simulates a government-led increase in housing supply",
        )
        stamp_duty_cut = st.slider(
            "Stamp duty reduction (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=10,
            help="Models the price impact of reducing stamp duty",
        )

    with col2:
        st.markdown("**Transport Investment**")
        selected_city = st.selectbox(
            "Target city",
            options=sorted(df["city"].unique()),
            index=0,
        )
        transport_investment = st.slider(
            "Additional annual transport investment ($B)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.5,
            help="Simulates increased public transport funding",
        )
        new_lines = st.number_input(
            "New rail/BRT corridors",
            min_value=0,
            max_value=10,
            value=1,
            step=1,
        )

    st.divider()

    # Placeholder projected outcome panel
    st.subheader(f"Projected Outcome — {selected_city}")

    baseline = df[(df["city"] == selected_city) & (df["year"] == selected_year)]
    if not baseline.empty:
        base_price     = baseline["median_house_price"].values[0]
        base_transport = baseline["transport_patronage_per_capita"].values[0]

        # Very rough illustrative model — replace with real elasticity estimates
        simulated_price_reduction  = base_price     * (supply_increase / 100) * 0.08
        simulated_patronage_uplift = base_transport * (transport_investment / 5) * 0.15

        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                label="Estimated Price Reduction",
                value=f"${simulated_price_reduction:,.0f}",
                delta=f"-{simulated_price_reduction / base_price * 100:.1f}%",
                delta_color="inverse",
            )
        with c2:
            st.metric(
                label="Estimated Patronage Uplift",
                value=f"+{simulated_patronage_uplift:.1f} boardings/capita",
                delta=f"+{simulated_patronage_uplift / base_transport * 100:.1f}%",
            )

    st.caption(
        "⚠️ These projections use simplified illustrative multipliers. "
        "A proper model requires elasticity estimates from peer-reviewed literature."
    )


# ===========================================================================
# Router — render the selected page
# ===========================================================================

if page == "The Story":
    page_the_story()
elif page == "Explore the Data":
    page_explore_data()
elif page == "What If?":
    page_what_if()
