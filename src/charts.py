"""
charts.py
---------
All Plotly visualisation functions for the Liveability Gap app.
Each function is self-contained: it accepts a DataFrame and returns a
`plotly.graph_objects.Figure` that Streamlit renders via `st.plotly_chart()`.

Design decisions:
  - Consistent colour palette tied to the Streamlit dark theme
  - `template="plotly_dark"` ensures axes/backgrounds match the app
  - City colours are fixed across all charts so the audience builds
    a stable visual vocabulary (same city → same colour everywhere)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Shared colour map — one colour per city, used consistently across all charts
# ---------------------------------------------------------------------------
CITY_COLOURS: dict[str, str] = {
    "Sydney":    "#E63946",  # red — largest, most expensive city
    "Melbourne": "#457B9D",  # blue
    "Brisbane":  "#F4A261",  # orange
    "Adelaide":  "#2A9D8F",  # teal
    "Perth":     "#E9C46A",  # yellow
    "Hobart":    "#A8DADC",  # light blue
    "Darwin":    "#C77DFF",  # purple
    "Canberra":  "#90BE6D",  # green
}

# Plotly template aligned with the dark Streamlit theme
_TEMPLATE = "plotly_dark"

# Shared layout defaults — applied to every figure for visual consistency
_LAYOUT_DEFAULTS: dict = {
    "paper_bgcolor": "rgba(0,0,0,0)",   # transparent → blends with app bg
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font":          {"family": "Inter, sans-serif", "color": "#EAEAEA"},
    "legend":        {"bgcolor": "rgba(22,33,62,0.8)", "bordercolor": "#2a2a4a",
                      "borderwidth": 1},
    "margin":        {"t": 60, "b": 40, "l": 40, "r": 20},
}


def _apply_defaults(fig: go.Figure) -> go.Figure:
    """Apply shared layout defaults to any figure."""
    fig.update_layout(**_LAYOUT_DEFAULTS)
    return fig


# ---------------------------------------------------------------------------
# 1. Scatter — median price vs transport patronage per capita
# ---------------------------------------------------------------------------

def scatter_price_vs_transport(df: pd.DataFrame, year: int = 2025) -> go.Figure:
    """
    Scatter plot comparing median dwelling price against public transport
    usage per capita for a single year.

    Reveals the core tension of the narrative: cities with high prices
    do not always have proportionally high transport access.

    Parameters
    ----------
    df   : DataFrame from load_placeholder_data()
    year : Calendar year to display (default 2025)

    Returns
    -------
    go.Figure
    """
    # Filter to the selected year only
    filtered = df[df["year"] == year].copy()

    fig = px.scatter(
        filtered,
        x="transport_patronage_per_capita",
        y="median_house_price",
        color="city",
        color_discrete_map=CITY_COLOURS,
        size="population",           # bubble size → population context
        size_max=50,
        text="city",
        hover_data={
            "median_house_price":             ":$,.0f",
            "transport_patronage_per_capita": ":.1f",
            "dominant_mode":                  True,
            "population":                     ":,.0f",
            "city":                           False,
        },
        template=_TEMPLATE,
        title=f"Housing Price vs Transport Access — {year}",
        labels={
            "transport_patronage_per_capita": "Annual Boardings per Capita",
            "median_house_price":             "Median House Price (AUD)",
        },
    )

    # Move labels slightly above the marker so they don't overlap
    fig.update_traces(textposition="top center", marker={"line": {"width": 1,
                      "color": "#EAEAEA"}})

    # Reference line — national median house price approximation
    national_median = filtered["median_house_price"].median()
    fig.add_hline(
        y=national_median,
        line_dash="dot",
        line_color="#EAEAEA",
        opacity=0.4,
        annotation_text=f"National Median ≈ ${national_median:,.0f}",
        annotation_position="bottom right",
    )

    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# 2. Bubble map — liveability index by city on an Australia basemap
# ---------------------------------------------------------------------------

def map_liveability(df: pd.DataFrame, year: int = 2025) -> go.Figure:
    """
    Bubble map of Australia where each bubble represents a capital city.
    Bubble size = transport patronage per capita.
    Bubble colour = median house price (diverging scale).

    Gives the audience an immediate geographic orientation before they
    dive into the line and bar charts.

    Parameters
    ----------
    df   : DataFrame from load_placeholder_data()
    year : Calendar year to display (default 2025)

    Returns
    -------
    go.Figure
    """
    filtered = df[df["year"] == year].copy()

    fig = px.scatter_geo(
        filtered,
        lat="lat",
        lon="lon",
        size="transport_patronage_per_capita",
        color="median_house_price",
        color_continuous_scale="RdYlGn_r",  # red = expensive, green = affordable
        hover_name="city",
        hover_data={
            "median_house_price":             ":$,.0f",
            "transport_patronage_per_capita": ":.1f",
            "dominant_mode":                  True,
            "lat":                            False,
            "lon":                            False,
        },
        size_max=45,
        projection="natural earth",
        template=_TEMPLATE,
        title=f"Liveability Snapshot — {year}",
        labels={"median_house_price": "Median House Price (AUD)"},
    )

    # Zoom the map to Australia
    fig.update_geos(
        visible=False,
        resolution=50,
        scope="world",
        lataxis_range=[-45, -10],
        lonaxis_range=[110, 155],
        showland=True,
        landcolor="#16213E",
        showocean=True,
        oceancolor="#0F3460",
        showcountries=True,
        countrycolor="#2a2a4a",
        showcoastlines=True,
        coastlinecolor="#2a2a4a",
    )

    fig.update_coloraxes(colorbar_tickprefix="$", colorbar_tickformat=",.0f")
    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# 3. Line chart — house and unit price trends 2020–2025 by city
# ---------------------------------------------------------------------------

def line_price_trends(df: pd.DataFrame,
                      price_type: str = "median_house_price") -> go.Figure:
    """
    Multi-line time-series showing how median dwelling prices evolved
    from 2020 to 2025 across all capital cities.

    Highlights the post-pandemic price surge and regional divergence —
    a key chapter in the liveability narrative.

    Parameters
    ----------
    df         : DataFrame from load_placeholder_data()
    price_type : Column to plot — "median_house_price" or "median_unit_price"

    Returns
    -------
    go.Figure
    """
    label_map = {
        "median_house_price": "Median House Price (AUD)",
        "median_unit_price":  "Median Unit Price (AUD)",
    }
    y_label = label_map.get(price_type, price_type)

    fig = px.line(
        df,
        x="year",
        y=price_type,
        color="city",
        color_discrete_map=CITY_COLOURS,
        markers=True,
        hover_data={"dominant_mode": True},
        template=_TEMPLATE,
        title=f"Dwelling Price Trends by City — 2020 to 2025",
        labels={"year": "Year", price_type: y_label, "city": "City"},
    )

    # Highlight the COVID recovery period
    fig.add_vrect(
        x0=2020, x1=2022,
        fillcolor="#E63946",
        opacity=0.07,
        annotation_text="COVID Period",
        annotation_position="top left",
        line_width=0,
    )

    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    fig.update_xaxes(dtick=1)
    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# 4. Bar chart — transport patronage by mode and city (latest year)
# ---------------------------------------------------------------------------

def bar_transport_modes(df: pd.DataFrame, year: int = 2025) -> go.Figure:
    """
    Grouped bar chart showing total annual transport boardings per capita,
    broken down by dominant mode for each capital city.

    Illustrates infrastructure investment disparity — cities that invested
    in rail vs those that rely predominantly on buses.

    Parameters
    ----------
    df   : DataFrame from load_placeholder_data()
    year : Calendar year to display (default 2025)

    Returns
    -------
    go.Figure

    Note
    ----
    The placeholder dataset stores a single dominant_mode per city.
    Once real BITRE data is loaded, this chart should be updated to use
    actual per-mode boarding counts (bus, rail, light rail, ferry).
    """
    filtered = df[df["year"] == year].copy()

    # Sort cities by patronage descending for visual clarity
    filtered = filtered.sort_values("transport_patronage_per_capita",
                                    ascending=False)

    # Mode colour map — consistent visual language across the report
    mode_colours: dict[str, str] = {
        "Rail":      "#457B9D",
        "Tram/Rail": "#E9C46A",
        "Bus":       "#F4A261",
        "Ferry":     "#A8DADC",
    }

    fig = px.bar(
        filtered,
        x="city",
        y="transport_patronage_per_capita",
        color="dominant_mode",
        color_discrete_map=mode_colours,
        text="transport_patronage_per_capita",
        hover_data={"dominant_mode": True, "transport_patronage_total": ":,.0f"},
        template=_TEMPLATE,
        title=f"Annual Transport Boardings per Capita by City — {year}",
        labels={
            "city":                           "City",
            "transport_patronage_per_capita": "Boardings per Capita",
            "dominant_mode":                  "Primary Mode",
        },
    )

    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_yaxes(title_text="Annual Boardings per Capita")
    return _apply_defaults(fig)
