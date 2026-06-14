# Data Warehousing for Morons by DLH.io — Brandy's Burritos Dashboard
## dlh-data-warehousing-for-morons-dashboard

Greetings from your DLH.io team of data engineering, AI, and Analytics experts.

This is the application for the Brandy's Burritos operations dashboard for our tutorials, classes, and articles.

We've built this tutorial to help guide the world's engineers on the basics of data for operational reporting and ultimately AI enablement. 
We've initially used the Observable Framework to help simplify the guidance.

The training is key and the understanding is what will take you to the next level.

Be sure to sign up for all DLH.io, dbdeux, and other replated platforms and newsletters to stay up on the latest from our Data Lake and AI community.

This is an interactive operations dashboard for **Brandy's Burritos**, a fictitious multi-location restaurant chain. Built with [Observable Framework](https://observablehq.com/framework/) and powered by data from [MotherDuck](https://motherduck.com/) (cloud-native DuckDB) or other amazing OLAP and Data Lake and Data Warehousing platforms..

This project accompanies the **DLH.io × MotherDuck integration guide**, where readers connect a Google Sheets data source to MotherDuck through [DLH.io](https://dlh.io), then visualize the synchronized data in this dashboard.

## Dashboard Features

| Feature | Description |
|---------|-------------|
| **KPI Cards** | Net Sales, Total Tickets, Avg Ticket, Labor Cost % |
| **Location Selector** | Dropdown with "All Locations" and all 40 stores |
| **Store Map** | US & Canada map with sized/colored circles per store |
| **Daily Sales Trend** | Line chart with 7-day moving average |
| **Sales by Day Part** | Breakfast / Lunch / Dinner breakdown |
| **Sales by Region** | Horizontal bar chart across 5 regions |
| **Labor vs Sales** | Scatter plot with regression line, color-coded by region |
| **Day-of-Week Sales** | Average daily sales by weekday |
| **Menu Category Revenue** | Revenue breakdown from sample ticket data |
| **Store Performance Table** | Sortable table: rank, sales, labor cost, labor % |
| **Current vs Prior Year** | Monthly sales comparison |
| **Employee Count by Role** | Bar chart of staff distribution |

All charts are **interactive** — hover for tooltips, and the location dropdown filters every visualization.

## Quick Start (with Sample Data)

The repository includes sample Parquet data files so you can run the dashboard immediately without a MotherDuck account.

```bash
# 1. Clone the repository
git clone https://github.com/datalakehouse/dlh-data-warehousing-for-morons-dashboard.git
cd dlh-data-warehousing-for-morons-dashboard/course/dashboard/app

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

Open **http://localhost:5847** in your browser.

## Connecting to MotherDuck

Once you have synchronized data from DLH.io into your MotherDuck database, you can refresh the dashboard to use your live data.

### Prerequisites

- Python 3.9+ with `duckdb`, `pandas`, and `pyarrow` installed
- A MotherDuck account with an access token

```bash
pip install duckdb pandas pyarrow
```

### Get Your MotherDuck Token

1. Go to [app.motherduck.com](https://app.motherduck.com/)
2. Navigate to **Settings → Access Tokens**
3. Create or copy your token

### Refresh Data from MotherDuck

```bash
# Set your token (or add to a .env file)
export MOTHERDUCK_TOKEN="your_token_here"

# Optional: change the database name (default: my_db)
export MOTHERDUCK_DATABASE="my_db"
# Optional: change the database name (default: burritos_google_sheets)
export MOTHERDUCK_SCHEMA="burritos_google_sheets"


# Run the refresh script
python scripts/refresh-from-motherduck.py
```

To use MotherDuck as your source and run the dashboard all in one script, including venv; copy and paste the following into a terminal at the root of the cloned repository:

```bash
# Create a virtual environment
python3 -m venv venv
 
# Activate it
source venv/bin/activate        # macOS / Linux
#venv\Scripts\activate           # Windows

# Prerequisites
python -m pip install duckdb pandas pyarrow

# Set your token (or add to a .env file)
export MOTHERDUCK_TOKEN="<your MD token here>"

export MOTHERDUCK_DATABASE="my_db"
export MOTHERDUCK_SCHEMA="burritos_google_sheets"

# Run the refresh script
python course/dashboard/app/scripts/refresh-from-motherduck.py

# run the dashboard
npm run dev --prefix course/dashboard/app

# When done, deactivate
#deactivate
```

This will pull all tables from your database and write them as Parquet files into `src/data/`. The dashboard will automatically reflect the updated data when you run `npm run dev`.

### Using a `.env` File

Copy the example and fill in your token:

```bash
cp .env.example .env
# Edit .env and paste your MOTHERDUCK_TOKEN
```

Then source it before running the refresh script:

```bash
source .env
python scripts/refresh-from-motherduck.py
```

## Data Schema

The dashboard expects the following tables in your database (matching the DLH.io sync from Google Sheets):

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `locations` | 40 store locations across US & Canada | `store_id`, `latitude`, `longitude`, `region` |
| `menu_items` | 30 menu items with pricing | `menu_item_id`, `category`, `current_price` |
| `employees` | 423 employees with roles | `employee_id`, `home_store_id`, `role` |
| `sales_daily` | Daily sales by store and day-part | `transaction_date`, `store_id`, `net_sales` |
| `labor_daily` | Daily labor costs by employee | `work_date`, `store_id`, `labor_cost` |
| `sales_tickets_sample` | Sample ticket line items | `ticket_id`, `menu_item_id`, `line_amount` |

## Project Structure

```
dlh-data-warehousing-for-morons-dashboard/
├── README.md                          # This file
└── course/
    └── dashboard/
        └── app/
            ├── package.json           # Node.js dependencies
            ├── observablehq.config.js # Observable Framework config
            ├── .env.example           # Template for MotherDuck token
            ├── scripts/
            │   └── refresh-from-motherduck.py  # Data refresh script
            └── src/
                ├── index.md           # Dashboard page (Observable Markdown)
                └── data/
                    ├── locations.parquet
                    ├── menu_items.parquet
                    ├── employees.parquet
                    ├── sales_daily.parquet
                    ├── labor_daily.parquet
                    └── sales_tickets_sample.parquet
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start local development server (http://localhost:5847) |
| `npm run build` | Build the static site to `dist/` |
| `npm run clean` | Remove the `dist/` build output |

## How It Works

1. **Data Layer**: Parquet files in `src/data/` contain the restaurant data. These can be the bundled sample data or freshly pulled from the data warehouse.

2. **SQL Engine**: Observable Framework uses [DuckDB-WASM](https://duckdb.org/docs/api/wasm/overview) in the browser to load and query the Parquet files — no server-side database needed at runtime.

3. **Visualizations**: Built with [Observable Plot](https://observablehq.com/plot/), a concise API for exploratory data visualization. The map uses the Albers USA projection with data from [US Atlas](https://github.com/topojson/us-atlas).

4. **Interactivity**: The location dropdown selector uses Observable's reactive `view()` pattern — changing the selection automatically re-computes all dependent calculations and re-renders every chart.

## Technology Stack

- [Observable Framework](https://observablehq.com/framework/) — Static site generator for data apps
- [DuckDB-WASM](https://duckdb.org/docs/api/wasm/overview) — In-browser SQL analytics engine
- [Observable Plot](https://observablehq.com/plot/) — JavaScript visualization library
- [MotherDuck](https://motherduck.com/) — Cloud-native DuckDB (data source)
- [DLH.io](https://dlh.io) — Data integration platform (connects Google Sheets → MotherDuck)

Can we use a different OLAP database or Data Warehouse? Definitely. Submit a ticket/issue and we'll get that setup for you.

## License

See repository license.
