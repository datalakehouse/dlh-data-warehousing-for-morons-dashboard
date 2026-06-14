# Brandy's Burritos — Visualization Dashboard

Greetings from your DLH.io team of data engineering, AI, and Analytics experts.

This is the application for the Brandy's Burritos operations dashboard for our tutorials, classes, and articles.

We've built this tutorial to help guide the world's engineers on the basics of data for operational reporting and ultimately AI enablement. 
We've initially used the Observable Framework to help simplify the guidance.

The training is key and the understanding is what will take you to the next level.

Be sure to sign up for all DLH.io, dbdeux, and other replated platforms and newsletters to stay up on the latest from our Data Lake and AI community.

## Setup Instructions
We've kept the setup as basic as possible to launch quickly. Follow the general steps below:

```bash
npm install
npm run dev
```

Then open http://localhost:5847.

## Refreshing Data from MotherDuck

```bash
export MOTHERDUCK_TOKEN="your_token"
python scripts/refresh-from-motherduck.py
```

See the [root README](../../../README.md) for full instructions.
