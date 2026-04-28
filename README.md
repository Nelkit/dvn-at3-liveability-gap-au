# The Liveability Gap: Housing Affordability vs Transport Access in Australian Capital Cities

## Description

This project is a data narrative built with Streamlit and Plotly that examines
the growing tension between housing affordability and public transport access
across Australia's eight capital cities (2020–2025). Using median dwelling
price data from the ABS and transport patronage statistics from BITRE, the
application guides policy makers and infrastructure planners through an
interactive story — revealing which cities face the most acute liveability
crisis and modelling the potential impact of targeted interventions.

This is an academic project completed for the UTS Master of Data Science
(Data Visualisation and Narratives, AT3, 2025).

---

## Data Sources

| Dataset | Source | URL |
|---|---|---|
| Residential Property Price Indexes | ABS Cat. 6416.0 | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/latest-release |
| Urban Public Transport Statistics | BITRE | https://www.bitre.gov.au/statistics/cities/urban_public_transport |

> **Note:** The application currently runs on **synthetic placeholder data**
> that mirrors the real dataset structure. Place the real Excel files in
> `data/raw/` and implement `load_abs_data()` and `load_bitre_data()`
> in `src/data_loader.py` to switch to live data.

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
liveability-gap-au/
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore
├── .streamlit/
│   └── config.toml         # Dark theme configuration
├── data/
│   ├── raw/                # Original ABS and BITRE source files (git-ignored)
│   └── processed/          # Cleaned, merged CSVs ready for charting
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # Data loading and placeholder generation
│   └── charts.py           # Plotly chart functions
└── assets/
    └── style.css           # Custom CSS overrides
```

---

## Data Dictionary

| Column | Type | Description |
|---|---|---|
| `city` | str | Capital city name |
| `year` | int | Calendar year (2020–2025) |
| `median_house_price` | float | Median established house price, AUD |
| `median_unit_price` | float | Median unit / apartment price, AUD |
| `transport_patronage_total` | int | Total annual boardings, all modes |
| `population` | int | Estimated city population |
| `transport_patronage_per_capita` | float | Annual boardings per resident |
| `dominant_mode` | str | Primary public transport mode |
| `lat` / `lon` | float | City centroid coordinates |

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
