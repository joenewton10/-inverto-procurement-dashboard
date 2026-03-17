# EU Procurement Benchmark Dashboard (Portfolio Version)

## What this project shows

A production-style analytics dashboard built from large-scale public procurement data (TED Contract Award Notices, 2018-2023) to support benchmarking of spend, supplier patterns, and competition trends across Europe.

## Why this is relevant

This project demonstrates practical capability for roles in Sustainability Analytics, ESG, Climate/Data Analytics, and consulting environments where large public datasets must be transformed into decision-ready insights.

## Business questions answered

- How has procurement spending evolved year by year?
- Which countries and categories account for the highest spend?
- What is the contract type mix (Services, Supplies, Works)?
- How competitive are tenders over time (average number of bidders)?
- What share of awards go to SMEs vs large firms?

## What I built

- End-to-end data pipeline to process multi-million-row CSV input
- Memory-safe cleaning workflow with chunked processing
- Streamlit dashboard with interactive filters and KPI cards
- Plotly visualizations for spend trends, country/category rankings, and competition metrics
- Cloud-ready deployment setup for Streamlit Community Cloud

## Technical stack

- Python
- Pandas
- PyArrow
- Streamlit
- Plotly

## Data scale and engineering highlights

- Processed 4M+ award records
- Created optimized clean outputs in CSV and Parquet
- Handled parser edge cases and large-file constraints with streaming/chunked approaches
- Added robust date parsing and deployment-safe path handling

## Key outputs

- Interactive dashboard app
- Cleaned analytical dataset for reuse
- Reproducible load and transformation script

## Run locally

```powershell
& "c:/Users/Joe/Desktop/application/Job Application/.venv/Scripts/python.exe" -m streamlit run "c:/Users/Joe/Desktop/application/Job Application/project-for-applications/inverto-project/app.py"
```

## Files to review

- App: project-for-applications/inverto-project/app.py
- Data pipeline: project-for-applications/inverto-project/load_data.py
- Technical setup: README.md

## Candidate fit summary

This portfolio piece reflects strengths in:

- Data engineering for large datasets
- Analytical storytelling through dashboards
- Practical Python problem solving under real constraints
- Translating complex data into stakeholder-friendly insights
