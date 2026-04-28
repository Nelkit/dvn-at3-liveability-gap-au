"""
data_loader.py
--------------
Responsible for loading and preparing data for the Liveability Gap app.

REAL DATA SOURCES (replace placeholder functions below):
  - ABS Residential Property Price Indexes (Cat. 6416.0)
      URL: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/
             residential-property-price-indexes-eight-capital-cities/latest-release
      Format: Excel (.xlsx), Table 1 — Residential Property Price Indexes

  - BITRE Urban Public Transport Statistics
      URL: https://www.bitre.gov.au/statistics/cities/urban_public_transport
      Format: Excel (.xlsx), Sheet "Annual Data" — patronage by mode and city

Replace `load_placeholder_data()` with `load_abs_data()` and
`load_bitre_data()` once the real files are placed in data/raw/.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# City reference — coordinates used for the bubble map visualisation
# ---------------------------------------------------------------------------
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

# Dominant transport mode per city — reflects infrastructure character
DOMINANT_MODE: dict[str, str] = {
    "Sydney":    "Rail",
    "Melbourne": "Tram/Rail",
    "Brisbane":  "Bus",
    "Adelaide":  "Bus",
    "Perth":     "Rail",
    "Hobart":    "Bus",
    "Darwin":    "Bus",
    "Canberra":  "Bus",
}


def load_placeholder_data() -> pd.DataFrame:
    """
    Generate synthetic data that mirrors the structure of the real ABS and
    BITRE datasets.  Every column name and unit here matches what will be
    present once the real files are loaded — so the chart functions require
    no changes when the swap happens.

    Returns
    -------
    pd.DataFrame
        Columns:
          city                       (str)   Capital city name
          year                       (int)   Calendar year 2020–2025
          median_house_price         (float) Median dwelling price, AUD
          median_unit_price          (float) Median unit/apartment price, AUD
          transport_patronage_total  (int)   Annual boardings across all modes
          population                 (int)   Approximate city population
          transport_patronage_per_capita (float) boardings / population
          dominant_mode              (str)   Primary public-transport mode
          lat / lon                  (float) City centroid coordinates
    """
    rng = np.random.default_rng(seed=42)  # fixed seed → reproducible charts

    cities = list(CITY_COORDS.keys())
    years  = list(range(2020, 2026))

    # Base house prices (AUD) — approximate 2020 medians per city
    base_house: dict[str, float] = {
        "Sydney":    1_050_000,
        "Melbourne":   780_000,
        "Brisbane":    560_000,
        "Adelaide":    480_000,
        "Perth":       510_000,
        "Hobart":      500_000,
        "Darwin":      450_000,
        "Canberra":    700_000,
    }

    # Base unit prices — typically 60–75 % of house price
    base_unit: dict[str, float] = {c: v * 0.68 for c, v in base_house.items()}

    # Annual growth rates (house, unit) — vary by city to reflect boom/bust
    growth_rates: dict[str, tuple[float, float]] = {
        "Sydney":    (0.075, 0.055),
        "Melbourne": (0.060, 0.045),
        "Brisbane":  (0.090, 0.075),
        "Adelaide":  (0.085, 0.070),
        "Perth":     (0.095, 0.080),
        "Hobart":    (0.070, 0.060),
        "Darwin":    (0.040, 0.035),
        "Canberra":  (0.065, 0.050),
    }

    # Base annual public transport boardings (~2020, millions)
    base_patronage_m: dict[str, float] = {
        "Sydney":    390.0,
        "Melbourne": 450.0,
        "Brisbane":  160.0,
        "Adelaide":   65.0,
        "Perth":      95.0,
        "Hobart":      9.0,
        "Darwin":      3.5,
        "Canberra":   18.0,
    }

    # Approximate 2020 populations
    base_population: dict[str, int] = {
        "Sydney":    5_300_000,
        "Melbourne": 5_000_000,
        "Brisbane":  2_500_000,
        "Adelaide":  1_400_000,
        "Perth":     2_100_000,
        "Hobart":      240_000,
        "Darwin":      150_000,
        "Canberra":    450_000,
    }

    rows = []
    for city in cities:
        lat, lon = CITY_COORDS[city]
        h_rate, u_rate = growth_rates[city]

        for i, year in enumerate(years):
            # Compound price growth with small random noise
            noise_h = rng.uniform(0.95, 1.05)
            noise_u = rng.uniform(0.95, 1.05)
            house_price = base_house[city] * ((1 + h_rate) ** i) * noise_h
            unit_price  = base_unit[city]  * ((1 + u_rate) ** i) * noise_u

            # Patronage: COVID dip in 2020–21, recovery 2022–25
            covid_factor = 0.45 if year == 2020 else (0.60 if year == 2021 else
                           0.80 if year == 2022 else (0.90 if year == 2023 else
                           0.96 if year == 2024 else 1.00))
            patronage_noise = rng.uniform(0.97, 1.03)
            patronage = int(
                base_patronage_m[city] * 1_000_000 * covid_factor * patronage_noise
            )

            pop = int(base_population[city] * (1.015 ** i))  # ~1.5 % growth/yr
            patronage_per_capita = patronage / pop

            rows.append({
                "city":                        city,
                "year":                        year,
                "median_house_price":          round(house_price, 0),
                "median_unit_price":           round(unit_price,  0),
                "transport_patronage_total":   patronage,
                "population":                  pop,
                "transport_patronage_per_capita": round(patronage_per_capita, 2),
                "dominant_mode":               DOMINANT_MODE[city],
                "lat":                         lat,
                "lon":                         lon,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Stubs for real data loading — implement once files are in data/raw/
# ---------------------------------------------------------------------------

def load_abs_data(filepath: str) -> pd.DataFrame:
    """
    Load ABS Residential Property Price Indexes from the downloaded Excel file.

    Parameters
    ----------
    filepath : str
        Path to the ABS Cat. 6416.0 Excel file (e.g. 'data/raw/641601.xlsx').

    TODO: implement when real data is available.
    """
    raise NotImplementedError("Replace placeholder data with real ABS source.")


def load_bitre_data(filepath: str) -> pd.DataFrame:
    """
    Load BITRE urban public transport statistics from the downloaded Excel file.

    Parameters
    ----------
    filepath : str
        Path to the BITRE Excel file (e.g. 'data/raw/bitre_urban_transport.xlsx').

    TODO: implement when real data is available.
    """
    raise NotImplementedError("Replace placeholder data with real BITRE source.")
