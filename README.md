# Inverto Procurement Dashboard

Interactive Streamlit dashboard for benchmarking EU public procurement awards (TED Contract Award Notices, 2018-2023).

## Project Structure

- `project-for-applications/inverto-project/app.py`: Streamlit app
- `project-for-applications/inverto-project/load_data.py`: Data cleaning + CSV/parquet generation pipeline
- `project-for-applications/inverto-project/data/`: Data files
- `requirements.txt`: Python dependencies

## Features

- KPI overview: total contracts, total value, median contract value, buyer countries
- Time trend of contract value by year
- Spend split by contract type
- Top buyer countries and top CPV categories
- Competition metrics (average bids)
- SME vs large firm winner split
- Interactive filters for year, country, contract type, and CPV

## Local Setup (Windows PowerShell)

Use the existing virtual environment directly (activation is optional):

```powershell
& "c:/Users/Joe/Desktop/application/Job Application/.venv/Scripts/python.exe" -m pip install -r "c:/Users/Joe/Desktop/application/Job Application/requirements.txt"
```

## Run the App

```powershell
& "c:/Users/Joe/Desktop/application/Job Application/.venv/Scripts/python.exe" -m streamlit run "c:/Users/Joe/Desktop/application/Job Application/project-for-applications/inverto-project/app.py"
```

Then open: `http://localhost:8501`

## Data Preparation

Generate cleaned outputs:

```powershell
& "c:/Users/Joe/Desktop/application/Job Application/.venv/Scripts/python.exe" "c:/Users/Joe/Desktop/application/Job Application/project-for-applications/inverto-project/load_data.py"
```

This produces:

- `project-for-applications/inverto-project/data/ted_clean.csv`
- `project-for-applications/inverto-project/data/ted_clean.parquet`

## Streamlit Community Cloud Deployment

### 1. Push to GitHub

This repository is already initialized locally. Create the GitHub repo, then push:

```powershell
git -C "c:/Users/Joe/Desktop/application/Job Application" remote add origin https://github.com/<your-username>/<your-repo>.git
git -C "c:/Users/Joe/Desktop/application/Job Application" push -u origin main
```

### 2. Configure Streamlit Cloud

- Repository: `<your-username>/<your-repo>`
- Branch: `main`
- Main file path: `project-for-applications/inverto-project/app.py`

### 3. Data in Cloud

Large local data files are gitignored. The app supports two data sources:

- Local file in repo: `project-for-applications/inverto-project/data/ted_clean.parquet`
- Remote parquet URL using env var: `TED_PARQUET_URL`

Set `TED_PARQUET_URL` in Streamlit Cloud app settings if you do not commit parquet to the repo.

## Notes

- If PowerShell blocks activation scripts, run Python via full path as shown above.
- If dependencies change, update `requirements.txt` and re-run install.
