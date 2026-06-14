---
title: Brandy's Burritos Dashboard
toc: false
sql:
  locations: data/locations.parquet
  menu_items: data/menu_items.parquet
  employees: data/employees.parquet
  sales_daily: data/sales_daily.parquet
  labor_daily: data/labor_daily.parquet
  sales_tickets_sample: data/sales_tickets_sample.parquet
---

```js
import {html} from "npm:htl";
```

<!-- ───────── Load Data ───────── -->

```sql id=locationsRaw
SELECT * FROM locations
```

```sql id=salesDailyRaw
SELECT * FROM sales_daily
```

```sql id=laborDailyRaw
SELECT * FROM labor_daily
```

```sql id=menuItemsRaw
SELECT * FROM menu_items
```

```sql id=ticketsRaw
SELECT * FROM sales_tickets_sample
```

```js
const locations = [...locationsRaw];
const salesDaily = [...salesDailyRaw];
const laborDaily = [...laborDailyRaw];
const menuItems = [...menuItemsRaw];
const tickets = [...ticketsRaw];
```

<!-- ───────── Dashboard Layout ───────── -->
<div style="vw: 100; max-width: auto !important; font-size: 32px; font-weight: bold;">
  🌯 Brandy's Burritos — Operations Dashboard | Demo by DLH.io
</div>


<!-- ───────── Location Selector ───────── -->

```js
const locationOptions = [
  {label: "All Locations", value: "ALL"},
  ...locations.map(d => ({label: d.store_name, value: d.store_id}))
];
const selectedLocation = view(Inputs.select(locationOptions, {
  label: "Location",
  format: d => d.label,
  value: locationOptions[0]
}));
```

```js
const storeFilter = selectedLocation.value;
const filteredSales = storeFilter === "ALL"
  ? salesDaily
  : salesDaily.filter(d => d.store_id === storeFilter);
const filteredLabor = storeFilter === "ALL"
  ? laborDaily
  : laborDaily.filter(d => d.store_id === storeFilter);
const filteredTickets = storeFilter === "ALL"
  ? tickets
  : tickets.filter(d => d.store_id === storeFilter);
```

<!-- ───────── KPI Calculations ───────── -->

```js
const currentSales = filteredSales.filter(d => d.period_label === "Current");
const totalNetSales = currentSales.reduce((s, d) => s + (d.net_sales || 0), 0);
const totalTickets = currentSales.reduce((s, d) => s + (d.ticket_count || 0), 0);
const totalItems = currentSales.reduce((s, d) => s + (d.item_count || 0), 0);
const avgTicket = totalTickets > 0 ? totalNetSales / totalTickets : 0;
const totalLaborCost = filteredLabor.filter(d => d.period_label === "Current").reduce((s, d) => s + (d.labor_cost || 0), 0);
const laborPct = totalNetSales > 0 ? (totalLaborCost / totalNetSales) * 100 : 0;
const totalLoyalty = currentSales.reduce((s, d) => s + (d.loyalty_ticket_count || 0), 0);
const loyaltyPct = totalTickets > 0 ? (totalLoyalty / totalTickets) * 100 : 0;
```

<!-- ───────── Dashboard Layout ───────── -->

<div class="grid grid-cols-4" style="grid-auto-rows: auto;">
  <div class="card">
    <h2>Net Sales (Current)</h2>
    <span class="big">${totalNetSales.toLocaleString("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0})}</span>
  </div>
  <div class="card">
    <h2>Total Tickets</h2>
    <span class="big">${totalTickets.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Avg Ticket</h2>
    <span class="big">${avgTicket.toLocaleString("en-US", {style: "currency", currency: "USD"})}</span>
  </div>
  <div class="card">
    <h2>Labor Cost %</h2>
    <span class="big">${laborPct.toFixed(1)}%</span>
  </div>
</div>

<!-- ───────── Map ───────── -->

## Store Performance Map

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
<div class="card card-relative" style="padding: 1rem;">

```js
// Aggregate net sales per store for "Current" period
const salesByStore = new Map();
salesDaily.filter(d => d.period_label === "Current").forEach(d => {
  salesByStore.set(d.store_id, (salesByStore.get(d.store_id) || 0) + (d.net_sales || 0));
});

const mapData = locations.map(d => ({
  ...d,
  total_net_sales: salesByStore.get(d.store_id) || 0
}));

const maxSales = Math.max(...mapData.map(d => d.total_net_sales));
```

```js
Plot.plot({
  projection: {type: "albers-usa"},
  width: Math.min(628, window.innerWidth - 80),
  height: 320,
  color: {
    type: "linear",
    domain: [0, maxSales],
    scheme: "YlOrRd",
    label: "Net Sales ($)",
    legend: true
  },
  r: {range: [4, 30]},
  marks: [
    Plot.geo(await fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json").then(r => r.json()).then(us => topojson.feature(us, us.objects.states)), {
      stroke: "#ccc",
      fill: "#f8f8f8"
    }),
    Plot.dot(mapData.filter(d => d.country === "US"), {
      x: "longitude",
      y: "latitude",
      r: "total_net_sales",
      fill: "total_net_sales",
      stroke: "#333",
      strokeWidth: 0.5,
      tip: true,
      title: d => `${d.store_name}\n${d.city}, ${d.state_province}\nNet Sales: ${d.total_net_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    // Canada locations shown as annotations at top
    Plot.dot(mapData.filter(d => d.country === "CA"), {
      // Project Canadian lat/lon roughly into view
      x: d => d.longitude + 8,
      y: d => d.latitude - 4,
      r: "total_net_sales",
      fill: "total_net_sales",
      stroke: "#333",
      strokeWidth: 0.5,
      tip: true,
      title: d => `${d.store_name}\n${d.city}, ${d.state_province} (Canada)\nNet Sales: ${d.total_net_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    Plot.text(mapData.filter(d => d.country === "CA").slice(0, 1), {
      x: d => d.longitude + 8,
      y: d => d.latitude - 2,
      text: ["🇨🇦 Canada"],
      fontSize: 11,
      fill: "#666"
    })
  ]
})
```
</div>


<div class="card card-relative" style="padding: 1rem;">

## Sales by Day Part

```js
const dayPartData = Array.from(
  d3.rollup(
    currentSales,
    v => d3.sum(v, d => d.net_sales),
    d => d.day_part
  ),
  ([day_part, net_sales]) => ({day_part, net_sales})
).filter(d => d.net_sales > 0);
```

```js
Plot.plot({
  x: {label: "Day Part"},
  y: {grid: true, label: "Net Sales ($)", tickFormat: "$,.0f"},
  width: Math.min(480, window.innerWidth - 80),
  height: 340,
  color: {
    domain: ["Breakfast", "Lunch", "Dinner"],
    range: ["#f4a261", "#e76f51", "#264653"]
  },
  marks: [
    Plot.barY(dayPartData, {
      x: "day_part",
      y: "net_sales",
      fill: "day_part",
      tip: true,
      title: d => `${d.day_part}: ${d.net_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    Plot.ruleY([0])
  ]
})
```

</div>


</div> <!-- ...performance map section -->

<!-- ───────── Sales Trend ───────── -->

<div class="grid grid-cols-1" style="grid-auto-rows: auto;">
<div class="card">

## Daily Sales Trend

```js
// Aggregate sales by date for the current period
// Group by ISO date string to avoid Date reference equality issues
const salesByDate = Array.from(
  d3.rollup(
    currentSales.filter(d => d.day_part !== "Breakfast" || d.net_sales > 0),
    v => ({
      net_sales: d3.sum(v, d => d.net_sales),
      tickets: d3.sum(v, d => d.ticket_count)
    }),
    d => new Date(d.transaction_date).toISOString().slice(0, 10)
  ),
  ([dateStr, vals]) => ({date: new Date(dateStr + "T00:00:00"), ...vals})
).sort((a, b) => a.date - b.date);
```

```js
Plot.plot({
  y: {grid: true, label: "Net Sales ($)", tickFormat: "$,.0f"},
  x: {type: "utc", label: "Date"},
  width: 1200,
  height: 200,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(salesByDate, {
      x: "date",
      y: "net_sales",
      stroke: "#e25822",
      strokeWidth: 1.5,
      strokeOpacity: 0.5,
      curve: "catmull-rom"
    }),
    Plot.lineY(salesByDate, Plot.windowY(7, {
      x: "date",
      y: "net_sales",
      stroke: "#333",
      strokeWidth: 2.5
    })),
    Plot.text([{x: salesByDate[Math.floor(salesByDate.length * 0.8)]?.date, y: d3.max(salesByDate, d => d.net_sales) * 0.95}], {
      x: "x", y: "y", text: ["— 7-day avg"], fontSize: 10, fill: "#666"
    })
  ]
})
```

</div>
<!-- <div class="card"> -->

<!-- TODO: Add another graph/chart here - be clever -->

<!-- </div> -->
</div>

<!-- ───────── Sales by Region ───────── -->

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
<div class="card">

## Sales by Region

```js
const regionLookup = new Map(locations.map(d => [d.store_id, d.region]));
const regionSales = Array.from(
  d3.rollup(
    currentSales,
    v => d3.sum(v, d => d.net_sales),
    d => regionLookup.get(d.store_id) || "Unknown"
  ),
  ([region, net_sales]) => ({region, net_sales})
).sort((a, b) => b.net_sales - a.net_sales);
```

```js
Plot.plot({
  x: {grid: true, label: "Net Sales ($)", tickFormat: "$,.0f"},
  y: {label: "Region"},
  width: Math.min(580, window.innerWidth - 80),
  height: 280,
  marginLeft: 130,
  marks: [
    Plot.barX(regionSales, {
      y: "region",
      x: "net_sales",
      fill: "#e25822",
      sort: {y: "-x"},
      tip: true,
      title: d => `${d.region}: ${d.net_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    Plot.ruleX([0])
  ]
})
```

</div>
<div class="card">

## Labor vs Sales by Store

```js
const laborByStore = new Map();
laborDaily.filter(d => d.period_label === "Current").forEach(d => {
  laborByStore.set(d.store_id, (laborByStore.get(d.store_id) || 0) + (d.labor_cost || 0));
});

const storeComparison = locations.map(d => ({
  store_id: d.store_id,
  store_name: d.store_name.replace("Brandy's Burritos - ", ""),
  region: d.region,
  net_sales: salesByStore.get(d.store_id) || 0,
  labor_cost: laborByStore.get(d.store_id) || 0,
  labor_pct: (salesByStore.get(d.store_id) || 0) > 0
    ? ((laborByStore.get(d.store_id) || 0) / (salesByStore.get(d.store_id) || 0)) * 100
    : 0
}));
```

```js
Plot.plot({
  x: {label: "Net Sales ($)", tickFormat: "$,.0f"},
  y: {label: "Labor Cost ($)", tickFormat: "$,.0f"},
  r: {range: [3, 14]},
  color: {legend: true, label: "Region"},
  width: Math.min(580, window.innerWidth - 80),
  height: 280,
  marks: [
    Plot.dot(storeComparison, {
      x: "net_sales",
      y: "labor_cost",
      r: "labor_pct",
      fill: "region",
      stroke: "#333",
      strokeWidth: 0.3,
      tip: true,
      title: d => `${d.store_name}\n${d.region}\nSales: ${d.net_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}\nLabor: ${d.labor_cost.toLocaleString("en-US", {style: "currency", currency: "USD"})}\nLabor %: ${d.labor_pct.toFixed(1)}%`
    }),
    Plot.linearRegressionY(storeComparison, {
      x: "net_sales",
      y: "labor_cost",
      stroke: "#999",
      strokeDasharray: "4,4"
    })
  ]
})
```

</div>
</div>

<!-- ───────── Sales by Weekday ───────── -->

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
<div class="card">

## Sales by Day of Week

```js
const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const weekdaySales = Array.from(
  d3.rollup(
    currentSales,
    v => ({
      net_sales: d3.sum(v, d => d.net_sales),
      count: d3.count(v, d => d.net_sales)
    }),
    d => new Date(d.transaction_date).getDay()
  ),
  ([day, vals]) => ({day: dayNames[day], dayNum: day, avg_sales: vals.net_sales / (vals.count || 1)})
).sort((a, b) => a.dayNum - b.dayNum);
```

```js
Plot.plot({
  x: {label: "Day of Week", domain: dayNames},
  y: {grid: true, label: "Avg Daily Sales ($)", tickFormat: "$,.0f"},
  width: Math.min(580, window.innerWidth - 80),
  height: 280,
  marks: [
    Plot.barY(weekdaySales, {
      x: "day",
      y: "avg_sales",
      fill: d => d.dayNum === 5 || d.dayNum === 6 ? "#e25822" : "#2a9d8f",
      tip: true,
      title: d => `${d.day}: ${d.avg_sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    Plot.ruleY([0])
  ]
})
```

</div>
<div class="card">

## Menu Category Breakdown (Sample Tickets)

```js
const itemLookup = new Map(menuItems.map(d => [d.menu_item_id, d]));
const categorySales = Array.from(
  d3.rollup(
    filteredTickets,
    v => d3.sum(v, d => d.line_amount || 0),
    d => {
      const item = itemLookup.get(d.menu_item_id);
      return item ? item.category : "Unknown";
    }
  ),
  ([category, amount]) => ({category, amount})
).sort((a, b) => b.amount - a.amount);
```

```js
Plot.plot({
  x: {label: "Category"},
  y: {grid: true, label: "Revenue ($)", tickFormat: "$,.0f"},
  width: Math.min(580, window.innerWidth - 80),
  height: 280,
  color: {scheme: "Tableau10"},
  marks: [
    Plot.barY(categorySales, {
      x: "category",
      y: "amount",
      fill: "category",
      sort: {x: "-y"},
      tip: true,
      title: d => `${d.category}: ${d.amount.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    }),
    Plot.ruleY([0])
  ]
})
```

</div>
</div>

<!-- ───────── Top Stores Table ───────── -->

## Store Performance Summary

```js
const storeTableData = storeComparison
  .sort((a, b) => b.net_sales - a.net_sales)
  .map(d => ({
    "Store": d.store_name,
    "Region": d.region,
    "Net Sales": d.net_sales,
    "Labor Cost": d.labor_cost,
    "Labor %": d.labor_pct,
    "Sales Rank": 0
  }));
storeTableData.forEach((d, i) => d["Sales Rank"] = i + 1);
```

```js
// Apply store filter to the table if a specific store is selected
const tableData = storeFilter === "ALL"
  ? storeTableData
  : storeTableData.filter(d => {
      const loc = locations.find(l => l.store_id === storeFilter);
      return loc && d.Store === loc.store_name.replace("Brandy's Burritos - ", "");
    });
```

```js
Inputs.table(tableData, {
  columns: ["Sales Rank", "Store", "Region", "Net Sales", "Labor Cost", "Labor %"],
  header: {
    "Sales Rank": "#",
    "Net Sales": "Net Sales",
    "Labor Cost": "Labor Cost",
    "Labor %": "Labor %"
  },
  format: {
    "Net Sales": d => d.toLocaleString("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0}),
    "Labor Cost": d => d.toLocaleString("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0}),
    "Labor %": d => `${d.toFixed(1)}%`
  },
  sort: "Net Sales",
  reverse: true,
  width: {
    "Sales Rank": 50,
    "Store": 200,
    "Region": 140,
    "Net Sales": 120,
    "Labor Cost": 120,
    "Labor %": 80
  }
})
```

<!-- ───────── Current vs Prior Year ───────── -->

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
<div class="card">

## Current vs Prior Year — Monthly Sales

```js
// Compare current vs prior year by calendar month
const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const monthlyComp = Array.from(
  d3.rollup(
    filteredSales.filter(d => d.period_label === "Current" || d.period_label === "PriorYear"),
    v => d3.sum(v, d => d.net_sales),
    d => d.period_label,
    d => {
      const dt = new Date(d.transaction_date);
      return monthNames[dt.getUTCMonth()];
    }
  ),
  ([period, months]) => Array.from(months, ([month, sales]) => ({period, month, sales}))
).flat();
```

```js
Plot.plot({
  x: {label: "Month", domain: monthNames},
  y: {grid: true, label: "Net Sales ($)", tickFormat: "$,.0f"},
  color: {legend: true, domain: ["Current", "PriorYear"], range: ["#e25822", "#bbb"], label: "Period"},
  fx: {label: null},
  width: Math.min(580, window.innerWidth - 80),
  height: 300,
  marks: [
    Plot.barY(monthlyComp, Plot.groupX({y: "sum"}, {
      x: "month",
      y: "sales",
      fill: "period",
      tip: true,
      title: d => `${d.period} — ${d.month}\n${d.sales.toLocaleString("en-US", {style: "currency", currency: "USD"})}`
    })),
    Plot.ruleY([0])
  ]
})
```

</div>
<div class="card">

## Employee Count by Role

```js
const employeesFiltered = storeFilter === "ALL"
  ? locations.map(l => l.store_id)
  : [storeFilter];

// Count active employees from the employees data (note: loaded from parquet)
const empStoreFilter = new Set(employeesFiltered);
```

```sql id=employeesRaw
SELECT * FROM employees
```

```js
const employees = [...employeesRaw];
const activeEmps = employees.filter(d => d.active_flag === "Y" && (storeFilter === "ALL" || d.home_store_id === storeFilter));
const roleCounts = Array.from(
  d3.rollup(activeEmps, v => v.length, d => d.role),
  ([role, count]) => ({role, count})
).sort((a, b) => b.count - a.count);
```

```js
Plot.plot({
  x: {label: "Role"},
  y: {grid: true, label: "Count"},
  width: Math.min(580, window.innerWidth - 80),
  height: 280,
  marks: [
    Plot.barY(roleCounts, {
      x: "role",
      y: "count",
      fill: "#2a9d8f",
      sort: {x: "-y"},
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

</div>
</div>

<style>
.big {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
}
.card h2 {
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #666;
  margin: 0 0 0.5rem;
}
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.card h2,
.card h3 {
  align-self: stretch;
}
.card svg,
.card figure,
.card table,
.card form {
  max-width: 100%;
}
</style>
