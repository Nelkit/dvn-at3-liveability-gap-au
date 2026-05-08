"""
data_loader.py
--------------
Single source of truth for all data loading and transformation in the
Liveability Gap app.

Real data sources (pre-processed and joined in data/processed/):
  - ABS Residential Property Price Indexes (Cat. 6416.0)
      → data/processed/housing_prices_abs.csv
  - BITRE Urban Public Transport Statistics (Yearbook 2024, Table 5.3)
      → data/processed/passenger_km_bitre.csv
  - Cleaned + joined dataset (output of notebooks/data_cleaning.ipynb):
      → data/processed/liveability_gap_cleaned.csv  ← used by load_data()

Primary function: load_data()
  Reads the cleaned CSV, applies all derived transformations, and returns a
  single DataFrame consumed by every chart and KPI card in the app.

load_placeholder_data() is kept only as a DEPRECATED fallback.
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# City reference constants — used by both loaders and chart layers
# ---------------------------------------------------------------------------

# Geographic centroids — used by the bubble map visualisation
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Sydney":    (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Brisbane":  (-27.4698, 153.0251),
    "Adelaide":  (-34.9285, 138.6007),
    "Perth":     (-31.9505, 115.8605),
    "Hobart":    (-42.8821, 147.3272),
    "Darwin":    (-12.4634, 130.8456),
    "Canberra":  (-35.2809, 149.1300),
}

# 2024 estimated resident populations (ABS) — denominator for per-capita metrics
CITY_POPULATIONS: dict[str, int] = {
    "Sydney":    5_400_000,
    "Melbourne": 5_200_000,
    "Brisbane":  2_700_000,
    "Adelaide":  1_400_000,
    "Perth":     2_300_000,
    "Hobart":      240_000,
    "Darwin":      150_000,
    "Canberra":    470_000,
}

# Transport mode columns that constitute "public transport" (excludes private cars)
PUBLIC_TRANSPORT_MODES: list[str] = [
    "pkm_heavy_rail",
    "pkm_light_rail",
    "pkm_bus",
    "pkm_ferry",
]

# All per-mode columns available in the cleaned dataset — used by the stacked bar chart
ALL_MODE_COLS: list[str] = PUBLIC_TRANSPORT_MODES + [
    "pkm_passenger_cars",
    "pkm_commercial_vehicles",
    "pkm_motor_cycles",
    "pkm_other_active",
]

# Expected columns in the output DataFrame — guarantees chart compatibility
EXPECTED_COLUMNS: list[str] = [
    "city", "year", "financial_year",
    "median_house_price",
    "pkm_total", "pkm_public_transport", "pkm_public_transport_per_capita",
    "pkm_heavy_rail", "pkm_light_rail", "pkm_bus", "pkm_ferry",
    "pkm_passenger_cars", "pkm_commercial_vehicles", "pkm_motor_cycles",
    "pkm_other_active",
    "city_population", "liveability_gap_index", "dominant_mode",
    "lat", "lon",
]


# ---------------------------------------------------------------------------
# Primary loader — used by the entire app
# ---------------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    """
    Load the cleaned liveability dataset and apply all derived transformations.

    Reads data/processed/liveability_gap_cleaned.csv (produced by
    notebooks/data_cleaning.ipynb), then computes additional columns
    required by the app's charts and KPI cards.

    Returns
    -------
    pd.DataFrame
        One row per city-year combination. Columns:

        Identifiers
          city                         str    Capital city name
          year                         int    Financial year start (e.g. 2002)
          financial_year               str    FY label (e.g. "2002-03")

        Housing
          median_house_price           float  Median established house price (AUD)

        Transport — raw modes (billion km/year)
          pkm_total                    float  All modes combined
          pkm_heavy_rail               float  Heavy rail
          pkm_light_rail               float  Light rail
          pkm_bus                      float  Bus
          pkm_ferry                    float  Ferry
          pkm_passenger_cars           float  Private passenger cars
          pkm_commercial_vehicles      float  Commercial vehicles
          pkm_motor_cycles             float  Motorcycles
          pkm_other_active             float  Cycling + e-mobility

        Derived metrics
          pkm_public_transport         float  Heavy rail + light rail + bus + ferry
          city_population              int    2024 estimated resident population
          pkm_public_transport_per_capita float  PT km per person per year
          liveability_gap_index        float  price_norm − transport_norm in [−1, 1]
                                              Higher = more expensive AND less connected
          dominant_mode                str    The PT sub-mode with highest km that row

        Geography
          lat / lon                    float  City centroid coordinates

    Notes
    -----
    If the source file is missing, an empty DataFrame with all expected
    columns is returned and a warning is logged — the app will not crash.
    """
    csv_path = Path(__file__).parent.parent / "data" / "processed" / "liveability_gap_cleaned.csv"

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        logger.warning(
            "liveability_gap_cleaned.csv not found at %s. "
            "Returning empty DataFrame — run notebooks/data_cleaning.ipynb first.",
            csv_path,
        )
        # Return an empty but schema-correct DataFrame so the app degrades gracefully
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # ------------------------------------------------------------------
    # Step 1 — Convert price from $'000 to full AUD
    # ------------------------------------------------------------------
    # The source CSV stores prices in thousands (e.g. 850 means $850,000).
    # All dollar displays in the app use full AUD, so we multiply here once.
    df["median_house_price"] = df["median_house_price_000"] * 1_000
    df = df.drop(columns=["median_house_price_000"])

    # ------------------------------------------------------------------
    # Step 2 — Aggregate public transport kilometres
    # ------------------------------------------------------------------
    # Sum the four PT modes; fillna(0) handles cities without ferry/light rail
    # (e.g. Adelaide has no ferry) without propagating NaN into the aggregate.
    df["pkm_public_transport"] = (
        df[PUBLIC_TRANSPORT_MODES].fillna(0).sum(axis=1)
    )

    # ------------------------------------------------------------------
    # Step 3 — Attach city population
    # ------------------------------------------------------------------
    # Population is fixed at 2024 values across all years; this is a
    # deliberate simplification — we are measuring transport supply, not
    # demand growth, and 2024 populations give the most relevant per-capita
    # context for the target audience (current buyers).
    df["city_population"] = df["city"].map(CITY_POPULATIONS)

    # ------------------------------------------------------------------
    # Step 4 — Compute per-capita public transport km
    # ------------------------------------------------------------------
    # pkm_public_transport is in BILLION km; multiply by 1e9 to get km,
    # then divide by population to get km per person per year.
    df["pkm_public_transport_per_capita"] = (
        (df["pkm_public_transport"] * 1e9) / df["city_population"]
    )

    # ------------------------------------------------------------------
    # Step 5 — Compute the Liveability Gap Index
    # ------------------------------------------------------------------
    # Normalise both dimensions to [0, 1] across the ENTIRE dataset
    # (not per year) so the index is comparable across time.
    #
    # price_norm:     1 = most expensive city-year in dataset
    # transport_norm: 1 = best-served city-year in dataset
    #
    # index = price_norm - transport_norm
    #   > 0 → residents pay a premium relative to transport received
    #   < 0 → well-served relative to price paid
    #   max possible = +1 (most expensive + worst transport)
    #   min possible = -1 (cheapest + best transport)

    price     = df["median_house_price"]
    transport = df["pkm_public_transport_per_capita"]

    price_range     = price.max()     - price.min()
    transport_range = transport.max() - transport.min()

    # Guard against zero-range edge case (all values identical)
    price_norm     = (price     - price.min())     / price_range     if price_range     > 0 else 0.0
    transport_norm = (transport - transport.min()) / transport_range if transport_range > 0 else 0.0

    df["liveability_gap_index"] = price_norm - transport_norm

    # ------------------------------------------------------------------
    # Step 6 — Derive dominant public transport mode per row
    # ------------------------------------------------------------------
    # For each city-year, the dominant PT mode is whichever of the four
    # PT sub-modes has the highest passenger-km.  This drives colour coding
    # in the bar chart and hover labels.
    mode_labels = {
        "pkm_heavy_rail": "Heavy Rail",
        "pkm_light_rail": "Light Rail",
        "pkm_bus":        "Bus",
        "pkm_ferry":      "Ferry",
    }
    # idxmax(axis=1) returns the column name of the highest value per row;
    # fillna handles rows where all PT modes are NaN (fall back to "Bus").
    df["dominant_mode"] = (
        df[PUBLIC_TRANSPORT_MODES]
        .fillna(0)
        .idxmax(axis=1)
        .map(mode_labels)
        .fillna("Bus")
    )

    # ------------------------------------------------------------------
    # Step 7 — Attach geographic coordinates
    # ------------------------------------------------------------------
    df["lat"] = df["city"].map({c: v[0] for c, v in CITY_COORDS.items()})
    df["lon"] = df["city"].map({c: v[1] for c, v in CITY_COORDS.items()})

    # ------------------------------------------------------------------
    # Step 8 — Final sort and column selection
    # ------------------------------------------------------------------
    df = df[EXPECTED_COLUMNS].sort_values(["city", "year"]).reset_index(drop=True)

    return df

