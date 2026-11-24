# The Liveability Gap: Housing Affordability vs Transport Access in Australian Capital Cities

> An interactive data narrative that exposes which Australian capital cities charge the most and invest the least in public transport, built with Streamlit, Plotly, and real ABS and BITRE data.

---

## Live Dashboard

**[https://dvn-at3-liveability-gap-au-hm3dpzjbyzjjwjpusmytrm.streamlit.app/](https://dvn-at3-liveability-gap-au-hm3dpzjbyzjjwjpusmytrm.streamlit.app/)**

---

## Description

A data narrative built with Streamlit and Plotly that examines the growing
tension between housing affordability and public transport access across
Australia's eight capital cities from 2020 to 2025.

The narrative follows **The Detective arc**: the app opens with a data anomaly
(the "crime scene"), then progressively reveals the culprit variable through
five interactive charts. The primary audience is real estate agents advising
interstate and first-home buyers who need liveability context beyond price
alone, and Ministry of Housing stakeholders evaluating where transport
investment is most urgently needed.

This is an academic project completed for the UTS Master of Data Science
(Data Visualisation and Narratives, AT3, 2026).

---

## Team
| Name | Role |
| --- | --- |
| Nelkit Chavez | Architect-Artist (hybrid) |
| Saurabh Sabharwal | Analyst-Orator (hybrid) |
| Nipun Mudgal | Artist-Analyst-Orator (hybrid) |
| Raunak Dhirajkumar Singh | Artist-Analyst-Orator (hybrid) |
| Shriram Gajanan Kulkarni | Architect-Artist-Analyst-Orator (hybrid) |
| Sheshan Munusamy Neelavathi | Artist-Architect (hybrid) |
| Masaki | Orator |

---

## Data Sources

| Dataset | Source | URL | File | Collection Date | Licence |
| --- | --- | --- | --- | --- | --- |
| Residential Property Price Indexes (Cat. 6416.0) | Australian Bureau of Statistics (ABS) | [abs.gov.au](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/latest-release) | `data/raw/643202.xlsx` | March 2025 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Urban Passenger Transport Statistics (Yearbook 2024, Table 5.3) | Bureau of Infrastructure, Transport and Regional Economics (BITRE) | [bitre.gov.au](https://www.bitre.gov.au/publications/2024/bitre-statistical-report-australian-infrastructure-statistics-yearbook-2024) | `data/raw/bitre-yearbook-2024-05-passengers.xlsx` | May 2024 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Both sources were extracted, cleaned, and joined in `notebooks/data_cleaning.ipynb`.
The output file `data/processed/liveability_gap_cleaned.csv` is the single data
input for all charts and KPI cards in the app.

---

## Narrative Arc — The Detective

**Arc chosen:** The Detective

**Justification:** The Detective arc was selected because the central finding of this dataset is a genuine anomaly: cities with the highest house prices are not necessarily the best-served by public transport. This counterintuitive result is more compelling when the audience discovers it through evidence rather than being told it upfront. The Martini Glass arc was considered but rejected because it requires a strong single conclusion, and our data has eight cities with different gap profiles that reward exploration. The Drill-Down arc was rejected because our audience (real estate agents and policy stakeholders) benefits more from the narrative tension of "something is wrong here" than from starting with a broad overview.

| Act | Chart function | Question answered |
| --- | --- | --- |
| Act 1 — The Crime Scene | `scatter_crime_scene` | Which cities are expensive AND poorly served? |
| Act 2 — The Verdict | `bar_liveability_gap` | How do cities rank on the gap index? |
| Act 3 — The Evidence | `line_price_trends` | How has each city's price trajectory diverged since 2002? |
| Act 4 — The Clues | `bar_transport_modes` | What does each city's transport mix look like? |
| Act 5 — The Map | `map_liveability` | Where is the gap widest, geographically? |

---

## Advanced Features

### Feature 1 — Context-Aware Filtering

The Reference Year slider in the sidebar is registered in `st.session_state` with an explicit `key="selected_year"`. Every element on every page (KPI cards, all five charts, the What If? baselines, and the anomaly callout text) reads from this shared state and updates simultaneously. The anomaly callout (`st.error`) is fully dynamic: it computes the worst-gap city and best-transport city from the filtered DataFrame on every render, so the text is always factually accurate for the selected year.

**Key files:** `app.py` lines 84-91 (slider), 258-270 (dynamic callout)

### Feature 2 — Visual Tooltips and Data-Driven Modals

All five Plotly charts use `customdata` + `hovertemplate` with explicit field formatting, built with `go.Scatter` / `go.Bar` rather than `px` wrappers. This approach gives full control over what appears in each tooltip. Below Chart 1, a `st.expander` reveals the full ranked table for the selected year (all 8 cities sorted by gap index, with formatted price, transport, and index columns), turning the expandable component into a genuine data-driven insight layer rather than static documentation.

**Key files:** `src/charts.py` lines 160-172, 292-295, 375-379, 478-481, 578-582; `app.py` lines 277-292

### Feature 3 — What-If Parameterization

The What If? page exposes four intervention sliders, all wired into the simulation model. Housing levers: supply increase and stamp duty cut, both reducing the baseline median house price. Transport levers: capital investment and new rail/BRT corridors, both increasing per-capita public transport km. Transport uplift is capped at 50% to prevent physically implausible outputs. The simulated gap index is recomputed using the same normalisation as `load_data()`, and all baselines come from real data for the selected city and year. The multipliers are illustrative and intended for exploratory use only. Output includes a before/after grouped bar chart (`go.Figure`) with hover showing raw values.

**Key files:** `app.py` lines 399-570

---

## How to Run Locally

### Step 0 — Prerequisites

Python 3.11 or later is required. The raw data files must be present in `data/raw/`
before running the notebook. They are not committed to the repository.

If `data/processed/liveability_gap_cleaned.csv` is not present (it is git-ignored),
run the cleaning notebook first:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/data_cleaning.ipynb
```

### Step 1 — Clone the repository

```bash
git clone https://github.com/Nelkit/dvn-at3-liveability-gap-au
cd dvn-at3-liveability-gap-au
```

### Step 2 — Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the app

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
│   ├── raw/                      # Original ABS and BITRE Excel files (git-ignored)
│   └── processed/
│       ├── housing_prices_abs.csv        # Extracted ABS housing prices
│       ├── passenger_km_bitre.csv        # Extracted BITRE transport data
│       └── liveability_gap_cleaned.csv   # Cleaned and joined dataset (app input, git-ignored)
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
4. Computes `pkm_public_transport_per_capita` = (PT billion km x 1e9) / population
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

## Credits

### Academic

- **Subject:** Data Visualisation and Narratives (DVN AT3)
- **Institution:** University of Technology Sydney (UTS)
- **Year:** 2026
- **Group:** 8

### Data Licences

- Australian Bureau of Statistics (2025). *Residential Property Price Indexes: Eight Capital Cities* (Cat. 6416.0). Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Bureau of Infrastructure, Transport and Regional Economics (2024). *Australian Infrastructure Statistics Yearbook 2024 — Passenger Transport*. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

### Libraries and Tools

| Library | Version | Purpose |
| --- | --- | --- |
| Python | 3.11 | Runtime |
| Streamlit | >=1.35.0 | App framework and UI |
| Plotly | >=5.22.0 | Interactive charts |
| Pandas | >=2.2.0 | Data loading and transformation |
| NumPy | >=1.26.0 | Numerical operations |
| openpyxl | >=3.1.0 | Reading raw Excel source files |
| Jupyter | — | Data cleaning notebook |
