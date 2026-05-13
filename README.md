# The Liveability Gap: Housing Affordability vs Transport Access in Australian Capital Cities

## Description

A data narrative built with Streamlit and Plotly that examines the growing
tension between housing affordability and public transport access across
Australia's eight capital cities from 2001 to 2023.

The narrative follows **The Detective arc**: the app opens with a data anomaly
(the "crime scene"), then progressively reveals the culprit variable through
five interactive charts. The primary audience is real estate agents advising
interstate and first-home buyers who need liveability context beyond price
alone, and Ministry of Housing stakeholders evaluating where transport
investment is most urgently needed.

This is an academic project completed for the UTS Master of Data Science
(Data Visualisation and Narratives, AT3, 2026).

---

## Data Sources

| Dataset | Source | File |
| --- | --- | --- |
| Residential Property Price Indexes (Cat. 6416.0) | Australian Bureau of Statistics (ABS) | `data/raw/643202.xlsx` |
| Urban Passenger Transport Statistics (Yearbook 2024, Table 5.3) | Bureau of Infrastructure, Transport and Regional Economics (BITRE) | `data/raw/bitre-yearbook-2024-05-passengers.xlsx` |

Both sources were extracted, cleaned, and joined in `notebooks/data_cleaning.ipynb`.
The output file `data/processed/liveability_gap_cleaned.csv` is the single data
input for all charts and KPI cards in the app.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Nelkit/dvn-at3-liveability-gap-au
cd dvn-at3-liveability-gap-au
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Project Structure

```
dvn-at3-liveability-gap-au/
├── app.py                        # Streamlit entry point — routing and page layout
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .streamlit/
│   └── config.toml               # Dark theme and colour palette
├── data/
│   ├── raw/                      # Original ABS and BITRE Excel files
│   └── processed/
│       ├── housing_prices_abs.csv        # Extracted ABS housing prices
│       ├── passenger_km_bitre.csv        # Extracted BITRE transport data
│       └── liveability_gap_cleaned.csv   # Cleaned and joined dataset (app input)
├── notebooks/
│   └── data_cleaning.ipynb       # Extraction, cleaning, and joining pipeline
├── src/
│   ├── __init__.py
│   ├── data_loader.py            # load_data() — single data source for the app
│   └── charts.py                 # Plotly chart functions (5 charts, Detective arc)
└── assets/
    └── style.css                 # Custom CSS overrides
```

---

## Data Pipeline

```
data/raw/643202.xlsx
data/raw/bitre-yearbook-2024-05-passengers.xlsx
        |
        v
notebooks/data_cleaning.ipynb
        |
        v
data/processed/liveability_gap_cleaned.csv
        |
        v
src/data_loader.load_data()
        |
        v
app.py  (all pages and charts)
```

`load_data()` reads the cleaned CSV and applies the following transformations
before the DataFrame reaches any chart or KPI card:

1. Converts `median_house_price_000` from $'000 to full AUD
2. Sums `pkm_public_transport` = heavy rail + light rail + bus + ferry
3. Attaches `city_population` (2024 ABS estimates)
4. Computes `pkm_public_transport_per_capita` = (PT billion km × 1e9) / population
5. Computes `liveability_gap_index` (see below)
6. Derives `dominant_mode` = the PT sub-mode with the highest km per row
7. Attaches `lat` / `lon` city coordinates

---

## Liveability Gap Index

The index is the core analytical metric of this project. It quantifies how
much a city "overcharges" residents relative to the public transport access
it provides.

**Formula:**

```
price_norm     = (median_house_price - global_min) / (global_max - global_min)
transport_norm = (pkm_public_transport_per_capita - global_min) / (global_max - global_min)

liveability_gap_index = price_norm - transport_norm
```

Both dimensions are min-max normalised across the **entire dataset**
(8 cities x 23 years = 184 rows), not per year. This makes the index
comparable across time.

**Interpretation:**

| Value | Meaning |
| --- | --- |
| Close to +1 | Most expensive AND worst transport in the dataset |
| Close to 0 | Price and transport access are proportional |
| Close to -1 | Most affordable AND best transport in the dataset |

**Normalisation anchors (from real data):**

| Dimension | Minimum | Maximum |
| --- | --- | --- |
| Price | $120,150 — Hobart 2001 | $1,410,500 — Sydney 2023 |
| Transport | 307 km/capita — Canberra 2021 | 1,940 km/capita — Sydney 2018 |

**Worked example — Canberra FY 2019-20:**

```
median_house_price              = $720,250
pkm_public_transport_per_capita = 457 km/capita

price_norm     = (720,250 - 120,150) / (1,410,500 - 120,150) = 0.465
transport_norm = (457 - 307)         / (1,940 - 307)         = 0.092

liveability_gap_index = 0.465 - 0.092 = 0.37
```

Canberra scores 0.37 because it is the second most expensive city in the
dataset yet has less public transport per capita than Perth and Adelaide,
which are considerably cheaper.

---

## Data Dictionary

### liveability_gap_cleaned.csv (app input)

| Column | Type | Description | Unit |
| --- | --- | --- | --- |
| `city` | str | Australian capital city name | |
| `year` | int | Financial year start (e.g. 2002 = FY 2002-03) | |
| `financial_year` | str | FY label (e.g. "2002-03") | |
| `median_house_price` | float | Median established house price | AUD |
| `pkm_total` | float | Total passenger km, all modes | billion km/year |
| `pkm_public_transport` | float | Heavy rail + light rail + bus + ferry | billion km/year |
| `pkm_public_transport_per_capita` | float | PT km per resident per year | km/year |
| `pkm_heavy_rail` | float | Heavy rail passenger km | billion km/year |
| `pkm_light_rail` | float | Light rail passenger km | billion km/year |
| `pkm_bus` | float | Bus passenger km | billion km/year |
| `pkm_ferry` | float | Ferry passenger km | billion km/year |
| `pkm_passenger_cars` | float | Private car km | billion km/year |
| `pkm_commercial_vehicles` | float | Commercial vehicle km | billion km/year |
| `pkm_motor_cycles` | float | Motorcycle km | billion km/year |
| `pkm_other_active` | float | Cycling and e-mobility km | billion km/year |
| `city_population` | int | 2024 estimated resident population | persons |
| `liveability_gap_index` | float | Price norm minus transport norm | [-1, 1] |
| `dominant_mode` | str | PT sub-mode with highest km that row | |
| `lat` / `lon` | float | City centroid coordinates | degrees |

---

## Narrative Arc — The Detective

| Act | Chart | Question answered |
| --- | --- | --- |
| Act 1 — The Crime Scene | `scatter_crime_scene` | Which cities are expensive AND poorly served? |
| Act 2 — The Verdict | `bar_liveability_gap` | How do cities rank on the gap index? |
| Act 3 — The Evidence | `line_price_trends` | How has each city's price trajectory diverged since 2002? |
| Act 4 — The Clues | `bar_transport_modes` | What does each city's transport mix look like? |
| Act 5 — The Map | `map_liveability` | Where is the gap widest, geographically? |

---

## Credits

- **Group:** 8
- **Students:**
  - Nelkit Chavez
  - Saurabh Sabharwal
  - Nipun Mudgal
  - Raunak Dhirajkumar Singh
  - Shriram Gajanan Kulkarni
  - Sheshan Munusamy Neelavathi
  - Masaki
- **Subject:** Data Visualisation and Narratives (DVN AT3)
- **Institution:** University of Technology Sydney (UTS)
- **Year:** 2026
- **Tools:** Python · Streamlit · Plotly · Pandas · NumPy
