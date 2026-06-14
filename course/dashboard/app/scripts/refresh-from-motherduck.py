#!/usr/bin/env python3
"""
Refresh local Parquet data files from a MotherDuck database.

This script connects to your MotherDuck account, reads each table from the
configured database, and writes them as Parquet files into src/data/ so the
Observable Framework dashboard can visualize them.

Prerequisites:
  pip install duckdb pandas pyarrow

Usage:
  export MOTHERDUCK_TOKEN="your_token_here"
  python scripts/refresh-from-motherduck.py

Options (environment variables):
  MOTHERDUCK_TOKEN    - (required) Your MotherDuck access token
  MOTHERDUCK_DATABASE - (optional) Database name, defaults to "my_db"
  MOTHERDUCK_SCHEMA   - (optional) Schema name, defaults to "burritos_google_sheets"
"""

import duckdb
import os
import re
import sys
import pathlib
import pandas as pd

MOTHERDUCK_TOKEN = os.environ.get("MOTHERDUCK_TOKEN", "")
MOTHERDUCK_DATABASE = os.environ.get("MOTHERDUCK_DATABASE", "my_db")
MOTHERDUCK_SCHEMA = os.environ.get("MOTHERDUCK_SCHEMA", "burritos_google_sheets")

TABLES = [
    "locations",
    "menu_items",
    "employees",
    "sales_daily",
    "labor_daily",
    "sales_tickets_sample",
]

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "src" / "data"

# Columns that contain currency-formatted strings (e.g. "$1,234.56") from DLH.io
# and need to be converted to numeric floats for the dashboard.
CURRENCY_COLUMNS = {
    "gross_sales", "discount_total", "tax_total", "net_sales",
    "hourly_rate", "labor_cost", "current_price", "line_amount",
}

# DLH.io metadata columns to drop
DLH_META_COLUMNS = {"__row_md5", "__dlh_sync_ts"}

# Comma-formatted numeric columns (e.g. "2,400") to convert
COMMA_NUMERIC_COLUMNS = {"square_footage"}


def normalize_dlh_dataframe(df):
    """Normalize a DataFrame from DLH.io/MotherDuck to match dashboard expectations."""
    # 1. Lowercase all column names
    df.columns = [c.lower() for c in df.columns]

    # 2. Drop DLH metadata columns
    drop_cols = [c for c in df.columns if c in DLH_META_COLUMNS]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 3. Convert currency string columns to float
    for col in CURRENCY_COLUMNS & set(df.columns):
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[\$,]", "", regex=True)
            .str.strip()
            .replace("", "0")
            .astype(float)
        )

    # 4. Convert comma-formatted numeric columns to float
    for col in COMMA_NUMERIC_COLUMNS & set(df.columns):
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
            .replace("", "0")
            .astype(float)
        )

    return df


def main():
    if not MOTHERDUCK_TOKEN:
        print("Error: MOTHERDUCK_TOKEN environment variable is not set.")
        print("Get your token from: https://app.motherduck.com/ → Settings → Access Tokens")
        print()
        print("Usage:")
        print('  export MOTHERDUCK_TOKEN="your_token_here"')
        print("  python scripts/refresh-from-motherduck.py")
        sys.exit(1)

    conn_str = f"md:{MOTHERDUCK_DATABASE}?motherduck_token={MOTHERDUCK_TOKEN}"

    print(f"Connecting to MotherDuck database: {MOTHERDUCK_DATABASE}, schema: {MOTHERDUCK_SCHEMA} ...")
    try:
        con = duckdb.connect(conn_str)
    except Exception as e:
        print(f"Error connecting to MotherDuck: {e}")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUT_DIR}\n")

    for table in TABLES:
        try:
            qualified_table = f"{MOTHERDUCK_SCHEMA}.{table}"
            df = con.execute(f"SELECT * FROM {qualified_table}").fetchdf()
            df = normalize_dlh_dataframe(df)
            out_path = OUT_DIR / f"{table}.parquet"
            df.to_parquet(out_path, index=False)
            print(f"  ✓ {table}: {len(df):,} rows, {len(df.columns)} cols → {out_path.name}")
        except Exception as e:
            print(f"  ✗ {table}: {e}")

    con.close()
    print("\nDone! Run 'npm run dev' to preview the updated dashboard.")


if __name__ == "__main__":
    main()