"""
Data extraction scripts for DVN AT3 — Liveability Gap AU.

Outputs:
  data/processed/housing_prices_abs.csv   — from 643202.xlsx > Data1
  data/processed/passenger_km_bitre.csv   — from bitre-yearbook-2024-05-passengers.xlsx > Table 5.3a-j
"""

import csv
import datetime
from pathlib import Path

import openpyxl

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. 643202.xlsx — Data1 (ABS housing price transfers, quarterly)
# ---------------------------------------------------------------------------

def _parse_col_label(raw_label: str) -> tuple[str, str, str]:
    """Parse 'Metric ; City ;' into (metric, dwelling_type, city).

    The ABS header looks like:
      'Median Price of Established House Transfers (Unstratified) ;  Sydney ;'
    We extract city from the last ';' segment and derive dwelling_type from
    whether the metric mentions 'House' or 'Attached Dwelling'.
    """
    parts = [p.strip() for p in raw_label.split(";") if p.strip()]
    metric_full = parts[0] if parts else raw_label
    city = parts[-1] if len(parts) > 1 else ""

    if "Established House" in metric_full:
        dwelling_type = "Established House"
        metric = metric_full.replace("Established House Transfers (Unstratified)", "").strip().rstrip(";").strip()
    elif "Attached Dwelling" in metric_full:
        dwelling_type = "Attached Dwelling"
        metric = metric_full.replace("Attached Dwelling Transfers (Unstratified)", "").strip().rstrip(";").strip()
    else:
        dwelling_type = ""
        metric = metric_full

    # Simplify metric label
    if "Median Price" in metric:
        metric = "Median Price"
    elif "Number" in metric:
        metric = "Number of Transfers"

    return metric, dwelling_type, city


def extract_housing_prices():
    wb = openpyxl.load_workbook(RAW / "643202.xlsx", read_only=True, data_only=True)
    ws = wb["Data1"]
    rows = list(ws.iter_rows(values_only=True))

    # Row index 0  = metric+city labels
    # Row index 1  = unit
    # Row index 9  = Series ID
    # Row index 10+ = data (datetime, values…)
    header_row = rows[0]
    unit_row = rows[1]

    # Pre-parse each column: (metric, dwelling_type, city, unit)
    col_meta: list[tuple[str, str, str, str]] = []
    for i, cell in enumerate(header_row[1:], start=1):
        if not cell:
            col_meta.append(("", "", "", ""))
            continue
        metric, dwelling_type, city = _parse_col_label(str(cell))
        unit = str(unit_row[i]).strip() if i < len(unit_row) and unit_row[i] else ""
        col_meta.append((metric, dwelling_type, city, unit))

    # Output: long format — one row per (date, city, dwelling_type, metric)
    out_path = OUT / "housing_prices_abs.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "city", "dwelling_type", "metric", "unit", "value"])
        for row in rows[10:]:
            if row[0] is None:
                continue
            date_val = row[0]
            date_str = (
                date_val.strftime("%Y-%m-%d")
                if isinstance(date_val, datetime.datetime)
                else str(date_val)
            )
            for col_i, (metric, dwelling_type, city, unit) in enumerate(col_meta, start=1):
                if not city:
                    continue
                value = row[col_i] if col_i < len(row) else None
                writer.writerow([date_str, city, dwelling_type, metric, unit, value])

    wb.close()
    print(f"[OK] housing_prices_abs.csv  — {out_path}")


# ---------------------------------------------------------------------------
# 2. bitre-yearbook-2024-05-passengers.xlsx — Table 5.3a-j
#    Each sub-table: header row 3 cols, unit row 4, data rows 5+
#    Sub-tables separated by blank rows; next one starts with "Table 5.3x"
# ---------------------------------------------------------------------------

def extract_passenger_km():
    wb = openpyxl.load_workbook(
        RAW / "bitre-yearbook-2024-05-passengers.xlsx",
        read_only=True,
        data_only=True,
    )
    ws = wb["Table 5.3a-j"]
    rows = list(ws.iter_rows(values_only=True))

    # Locate sub-table start rows
    starts = []
    for i, row in enumerate(rows):
        if row[0] is not None and str(row[0]).startswith("Table 5.3"):
            starts.append(i)

    out_path = OUT / "passenger_km_bitre.csv"
    all_records = []

    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(rows)

        title = str(rows[start][0]).strip()
        # city name is after the em-dash
        city = title.split("—")[-1].strip() if "—" in title else title

        header_row_idx = start + 1   # "Financial year", "Passenger cars", …
        headers = [c for c in rows[header_row_idx] if c is not None]

        for row in rows[header_row_idx + 2 : end]:  # skip unit row (row +1)
            if row[0] is None or not str(row[0]).strip():
                continue
            record = {"city": city, "financial_year": str(row[0]).strip()}
            for col_i, col_name in enumerate(headers[1:], start=1):
                record[str(col_name).strip()] = row[col_i] if col_i < len(row) else None
            all_records.append(record)

    if all_records:
        # Union of all keys across sub-tables (order matters: preserve insertion order)
        fieldnames: list[str] = []
        seen: set[str] = set()
        for rec in all_records:
            for k in rec:
                if k not in seen:
                    fieldnames.append(k)
                    seen.add(k)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", restval="")
            writer.writeheader()
            writer.writerows(all_records)

    wb.close()
    print(f"[OK] passenger_km_bitre.csv  — {out_path}")


if __name__ == "__main__":
    extract_housing_prices()
    extract_passenger_km()
