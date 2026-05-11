"""
charts.py
---------
All Plotly visualisation functions for the Liveability Gap app.

Each function accepts a DataFrame produced by load_data() and returns a
plotly.graph_objects.Figure rendered by Streamlit via st.plotly_chart().

Narrative arc — The Detective:
  Chart 1 (scatter_crime_scene)  → Act 1: The Crime Scene   — the anomaly
  Chart 2 (bar_liveability_gap)  → Act 2: The Verdict       — ranking the gap
  Chart 3 (line_price_trends)    → Act 3: The Evidence      — price trajectory
  Chart 4 (bar_transport_modes)  → Act 4: The Clues         — mode breakdown
  Chart 5 (map_liveability)      → Act 5: Geographic reveal — where is it worst?

Design decisions:
    - template="plotly_white" so axes/backgrounds match the Streamlit light theme
  - Shared layout defaults applied via _apply_defaults() for visual consistency
  - City colours are FIXED across charts — the audience builds a stable visual
    vocabulary (same city → same colour in every view)
"""

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Shared design constants — mirror the .streamlit/config.toml palette
# ---------------------------------------------------------------------------

# One fixed colour per city — used consistently across all charts
CITY_COLOURS: dict[str, str] = {
    "Sydney":    "#E63946",  # red   — largest, most expensive city
    "Melbourne": "#457B9D",  # blue
    "Brisbane":  "#F4A261",  # orange
    "Adelaide":  "#2A9D8F",  # teal
    "Perth":     "#E9C46A",  # yellow
    "Hobart":    "#A8DADC",  # light blue
    "Darwin":    "#C77DFF",  # purple
    "Canberra":  "#90BE6D",  # green
}

# Colour scale for the gap index: green (low gap) → yellow → red (high gap)
GAP_COLORSCALE = [
    [0.0, "#2EC4B6"],   # teal  — affordable AND well-served
    [0.5, "#FFD166"],   # amber — middle ground
    [1.0, "#E63946"],   # red   — expensive AND poorly served
]

# App background colour — keeps chart backgrounds flush with the page
_BG = "#FFFFFF"

# Subtle grid line colour — visible but not distracting on light background
_GRID = "rgba(31,41,55,0.10)"

# Shared figure layout applied to every chart
_LAYOUT_DEFAULTS: dict = {
    "template": "plotly_white",
    "paper_bgcolor": "rgba(255,255,255,0)",    # transparent → blends with Streamlit bg
    "plot_bgcolor":  _BG,
    "font":          {"family": "sans-serif", "color": "#1F2937"},
    "legend":        {
        "bgcolor":     "rgba(255,255,255,0.85)",
        "bordercolor": "#E5E7EB",
        "borderwidth": 1,
    },
    "margin": {"t": 70, "b": 50, "l": 50, "r": 30},
}


def _apply_defaults(fig: go.Figure) -> go.Figure:
    """Apply shared layout defaults and subtle grid lines to any figure."""
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_xaxes(
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        showgrid=True,
    )
    fig.update_yaxes(
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        showgrid=True,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 1 — The Crime Scene scatter (FULLY IMPLEMENTED)
# ---------------------------------------------------------------------------

def scatter_crime_scene(df: pd.DataFrame, year: int) -> go.Figure:
    """
    Detective Arc — Act 1: The Crime Scene.

    Reveals the core anomaly driving this narrative: Australian capital cities
    that charge the highest house prices are NOT necessarily the ones with the
    best public transport access per capita.  The top-left quadrant (expensive
    AND poorly served) is where the liveability crisis is most acute.

    Designed for Real Estate Agent Sarah, who needs to show interstate buyers
    that price alone does not capture liveability — and for Ministry of Housing
    stakeholders who need to justify transport investment in high-cost cities.

    Parameters
    ----------
    df   : DataFrame from load_data()
    year : Financial year start integer to filter on (e.g. 2015 = FY 2015-16)

    Returns
    -------
    go.Figure
        Bubble scatter with quadrant annotations and reference lines.

    Expected input columns
    ----------------------
    city, year, median_house_price, pkm_public_transport_per_capita,
    city_population, liveability_gap_index
    """
    # Filter to the selected financial year only
    yr = df[df["year"] == year].copy()

    # ------------------------------------------------------------------
    # Reference lines — national medians split the chart into quadrants
    # ------------------------------------------------------------------
    # We use the median of city values (not population-weighted) so that
    # small cities like Hobart and Darwin are not drowned out by Sydney.
    nat_median_price     = yr["median_house_price"].median()
    nat_median_transport = yr["pkm_public_transport_per_capita"].median()

    # ------------------------------------------------------------------
    # Bubble sizing — sizeref scales bubbles relative to the largest city
    # ------------------------------------------------------------------
    # Plotly's sizeref formula: sizeref = 2 * max_value / desired_max_px²
    # Using 60 px as max diameter keeps Sydney readable without crowding.
    max_pop  = yr["city_population"].max()
    sizeref  = 2.0 * max_pop / (60 ** 2)

    # ------------------------------------------------------------------
    # Build the scatter trace manually (go.Scatter) so we can set
    # per-point colours from a continuous variable (liveability_gap_index)
    # while also controlling bubble size per point — px.scatter does not
    # support both simultaneously without workarounds.
    # ------------------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yr["pkm_public_transport_per_capita"],
        y=yr["median_house_price"],
        mode="markers+text",          # bubbles + city name labels
        text=yr["city"],              # label shown beside each bubble
        textposition="top center",    # position labels above bubbles to avoid overlap
        textfont={"color": "#1F2937", "size": 11},  # dark text, readable on light bg

        marker=dict(
            size=yr["city_population"],       # raw population → visual size
            sizemode="area",                  # area encoding is perceptually more accurate
            sizeref=sizeref,                  # normalises sizes relative to max city
            sizemin=8,                        # minimum pixel size so small cities stay visible
            color=yr["liveability_gap_index"],  # continuous colour = gap severity
            colorscale=GAP_COLORSCALE,
            showscale=True,
            colorbar=dict(
                title=dict(text="Gap Index", font={"color": "#1F2937"}),
                tickfont={"color": "#1F2937"},
                x=1.02,                       # nudge colorbar right so it doesn't overlap bubbles
            ),
            line=dict(width=1, color="#1F2937"),  # thin border improves legibility on light bg
        ),

        # Hover tooltip — City name + formatted key metrics
        customdata=list(zip(
            yr["city"],
            yr["median_house_price"],
            yr["pkm_public_transport_per_capita"],
            yr["liveability_gap_index"],
        )),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Median House Price: $%{customdata[1]:,.0f}<br>"
            "Transport km/capita: %{customdata[2]:,.0f}<br>"
            "Gap Index: %{customdata[3]:.2f}"
            "<extra></extra>"   # suppresses the default trace name box
        ),
    ))

    # ------------------------------------------------------------------
    # Horizontal reference line — national median house price
    # ------------------------------------------------------------------
    # Dashed so it reads as a reference, not a data series.
    fig.add_hline(
        y=nat_median_price,
        line_dash="dash",
        line_color="#1F2937",
        opacity=0.4,
        annotation_text=f"National Median Price  ${nat_median_price:,.0f}",
        annotation_position="bottom right",
        annotation_font={"color": "#1F2937", "size": 10},
    )

    # ------------------------------------------------------------------
    # Vertical reference line — national median transport per capita
    # ------------------------------------------------------------------
    fig.add_vline(
        x=nat_median_transport,
        line_dash="dash",
        line_color="#1F2937",
        opacity=0.4,
        annotation_text=f"National Median Transport  {nat_median_transport:,.0f} km",
        annotation_position="top left",
        annotation_font={"color": "#1F2937", "size": 10},
    )

    # ------------------------------------------------------------------
    # Quadrant annotations — orient the audience without an axis legend
    # ------------------------------------------------------------------
    # Placed as fractions of the axis range using paper coordinates.
    # xref/yref="paper" means 0=left/bottom edge, 1=right/top edge.
    # Small, italic, low-opacity so they don't compete with data points.
    quadrant_style = dict(
        xref="paper", yref="paper",
        showarrow=False,
        font={"size": 10, "color": "#6B7280", "style": "italic"},
        opacity=0.6,
    )

    fig.add_annotation(x=0.02, y=0.98, text="Expensive &amp; Poorly Served",
                       xanchor="left",  yanchor="top",    **quadrant_style)
    fig.add_annotation(x=0.98, y=0.98, text="Expensive but Connected",
                       xanchor="right", yanchor="top",    **quadrant_style)
    fig.add_annotation(x=0.02, y=0.02, text="Affordable but Isolated",
                       xanchor="left",  yanchor="bottom", **quadrant_style)
    fig.add_annotation(x=0.98, y=0.02, text="Affordable &amp; Connected",
                       xanchor="right", yanchor="bottom", **quadrant_style)

    # ------------------------------------------------------------------
    # Axis labels and title
    # ------------------------------------------------------------------
    fig.update_xaxes(
        title_text="Annual Public Transport km per Capita",
        tickformat=",",
    )
    fig.update_yaxes(
        title_text="Median House Price (AUD)",
        tickprefix="$",
        tickformat=",.0f",
    )

    # Financial year label reconstructed from start year (e.g. 2015 → "2015-16")
    fy_label = f"{year}-{str(year + 1)[-2:]}"
    fig.update_layout(title=dict(
        text=f"🔍 The Crime Scene — FY {fy_label}",
        font={"size": 18, "color": "#1F2937"},
    ))

    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# Chart 2 — Liveability Gap Ranking (TODO stub)
# ---------------------------------------------------------------------------

def bar_liveability_gap(df: pd.DataFrame, year: int) -> go.Figure:
    """
    Detective Arc — Act 2: The Verdict.

    Horizontal bar chart ranking all capital cities by liveability_gap_index
    for a given year.  High gap (red) = expensive AND poorly served by PT.

    # TODO: connect to real data — assigned to [team member]
    # Expected input columns: city, year, liveability_gap_index
    # Colors: #E63946 high gap, #2EC4B6 low gap

    Parameters
    ----------
    df   : DataFrame from load_data()
    year : Financial year start integer

    Returns
    -------
    go.Figure
    """
    # Guard: empty input
    yr = df[df["year"] == year].copy()
    if yr.empty:
        return _apply_defaults(go.Figure())

    # Aggregate / ensure one row per city (take mean if duplicates)
    grouped = (
        yr.groupby("city", as_index=False)["liveability_gap_index"]
        .mean()
    )

    # Sort descending so highest gap appears at top of the horizontal bar chart
    grouped = grouped.sort_values("liveability_gap_index", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=grouped["liveability_gap_index"],
        y=grouped["city"],
        orientation="h",
        marker=dict(
            color=grouped["liveability_gap_index"],
            colorscale=GAP_COLORSCALE,
            line=dict(color="#1F2937", width=0.5),
        ),
        customdata=list(zip(grouped["city"], grouped["liveability_gap_index"])),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Gap Index: %{customdata[1]:.2f}"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(
            text=f"Act 2 — Liveability Gap Ranking — FY {year}-{str(year + 1)[-2:]}",
            font={"size": 16, "color": "#1F2937"},
        ),
        xaxis=dict(title="Liveability Gap Index", range=[0, 1], tickformat=".2f"),
        yaxis=dict(autorange="reversed"),
    )

    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# Chart 3 — Price Trend Lines (TODO stub)
# ---------------------------------------------------------------------------
    """
    Detective Arc — Act 3: The Evidence.

    Multi-line time-series of median house price from 2002 to the latest year,
    one line per capital city.  A COVID shading band (2020–2022) is added to
    contextualise the post-pandemic price surge.

    # TODO: connect to real data — assigned to [team member]
    # Expected input columns: city, year, median_house_price
    # Add COVID shading 2020-2022

    Parameters
    ----------
    df        : DataFrame from load_data()
    price_col : Column to plot (default "median_house_price")

    Returns
    -------
    go.Figure
    """
    # TODO: connect to real data — assigned to [team member]
    # Expected input columns: city, year, median_house_price
    # Add COVID shading 2020-2022
def line_price_trends(df: pd.DataFrame, price_col: str = "median_house_price") -> go.Figure:
    """
    Detective Arc — Act 3: The Evidence.

    Multi-line time-series of median house price from 2002 to latest year,
    one line per capital city, with COVID shading from 2020–2022.
    """

    required_cols = {"city", "year", price_col}

    if df.empty or not required_cols.issubset(df.columns):
        return _apply_defaults(go.Figure())

    trend_df = df[["city", "year", price_col]].dropna().copy()
    trend_df = trend_df[trend_df["year"] >= 2002]
    trend_df = trend_df.sort_values(["city", "year"])

    if trend_df.empty:
        return _apply_defaults(go.Figure())

    fig = go.Figure()

    for city in sorted(trend_df["city"].unique()):

        city_df = trend_df[trend_df["city"] == city]

        fig.add_trace(
            go.Scatter(
                x=city_df["year"],
                y=city_df[price_col],
                mode="lines+markers",
                name=city,
                line=dict(
                    color=CITY_COLOURS.get(city, "#6B7280"),
                    width=2.6,
                ),
                marker=dict(size=5),
                customdata=list(zip(city_df["city"], city_df[price_col])),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Year: %{x}<br>"
                    "Median House Price: $%{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    # COVID shading band
    fig.add_vrect(
        x0=2020,
        x1=2022,
        fillcolor="rgba(128,128,128,0.20)",
        line_width=0,
        layer="below",
        annotation_text="COVID period",
        annotation_position="top left",
        annotation_font_size=11,
        annotation_font_color="#4B5563",
    )

    fig.update_layout(
        title=dict(
            text="Act 3 — The Evidence: Capital City House Price Trajectory",
            font={"size": 18, "color": "#1F2937"},
        ),
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=2,
        ),
        yaxis=dict(
            title="Median House Price (AUD)",
            tickprefix="$",
            tickformat=",.0f",
        ),
        hovermode="x unified",
        legend=dict(
            title="City",
            orientation="v",
        ),
        height=560,
    )

    return _apply_defaults(fig)


# ---------------------------------------------------------------------------
# Chart 4 — Transport Mode Mix (TODO stub)
# ---------------------------------------------------------------------------

def bar_transport_modes(df: pd.DataFrame, year: int) -> go.Figure:
    """
    Detective Arc — Act 4: The Clues.

    Stacked horizontal bar showing the transport mode mix (heavy rail, light
    rail, bus, ferry) for each capital city in the selected year.

    # TODO: connect to real data — assigned to [team member]
    # Expected input columns: city, year, pkm_heavy_rail,
    # pkm_light_rail, pkm_bus, pkm_ferry

    Parameters
    ----------
    df   : DataFrame from load_data()
    year : Financial year start integer

    Returns
    -------
    go.Figure
    """
    # TODO: connect to real data — assigned to [team member]
    # Expected input columns: city, year, pkm_heavy_rail,
    # pkm_light_rail, pkm_bus, pkm_ferry
    return go.Figure()


# ---------------------------------------------------------------------------
# Chart 5 — Geographic Bubble Map (FULLY IMPLEMENTED)
# ---------------------------------------------------------------------------

def map_liveability(df: pd.DataFrame, year: int) -> go.Figure:
    """
    Detective Arc — Act 5: Where Is the Gap Widest?

    Single tile map of Australia: each capital is a bubble at its centroid.
    Bubble area encodes public transport km per capita; colour encodes
    liveability_gap_index using the same `GAP_COLORSCALE` as Act 1 (fixed −1…1).

    Uses `go.Scattermap` with carto-positron tiles — no Mapbox token required.

    Parameters
    ----------
    df   : DataFrame from load_data()
    year : Financial year start integer (e.g. 2015 = FY 2015-16)

    Returns
    -------
    go.Figure

    Expected input columns
    ----------------------
    city, year, median_house_price, pkm_public_transport_per_capita,
    liveability_gap_index, lat, lon
    """
    yr = df[df["year"] == year].copy()
    if yr.empty:
        return _apply_defaults(go.Figure())

    max_pt = yr["pkm_public_transport_per_capita"].max()
    if pd.isna(max_pt) or max_pt <= 0:
        sizeref = 1.0
    else:
        sizeref = 2.0 * float(max_pt) / (55**2)

    fy_label = f"{year}-{str(year + 1)[-2:]}"

    fig = go.Figure()

    fig.add_trace(
        go.Scattermap(
            lat=yr["lat"],
            lon=yr["lon"],
            mode="markers+text",
            text=yr["city"],
            textposition="top center",
            textfont={"color": "#1F2937", "size": 11},
            marker=dict(
                size=yr["pkm_public_transport_per_capita"],
                sizemode="area",
                sizeref=sizeref,
                sizemin=10,
                color=yr["liveability_gap_index"],
                cmin=-1,
                cmax=1,
                colorscale=GAP_COLORSCALE,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Gap Index", font={"color": "#1F2937"}),
                    tickfont={"color": "#1F2937"},
                    x=1.02,
                ),
            ),
            customdata=list(
                zip(
                    yr["city"],
                    yr["median_house_price"],
                    yr["pkm_public_transport_per_capita"],
                    yr["liveability_gap_index"],
                )
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Median House Price: $%{customdata[1]:,.0f}<br>"
                "Transport km/capita: %{customdata[2]:,.0f}<br>"
                "Gap Index: %{customdata[3]:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=f"🗺️ Act 5 — Geographic Reveal — FY {fy_label}",
            font={"size": 18, "color": "#1F2937"},
        ),
        map=dict(
            style="carto-positron",
            center=dict(lat=-25.5, lon=134),
            zoom=3.15,
        ),
        height=520,
    )

    fig = _apply_defaults(fig)
    fig.update_layout(margin=dict(l=0, r=10, t=70, b=0))

    return fig
