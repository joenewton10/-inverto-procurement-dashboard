import pandas as pd
from pathlib import Path

FILE = r"C:\Users\Joe\Desktop\application\Job Application\project-for-applications\inverto-project\data\export_CAN_2023_2018.csv"

COLS = [
    "YEAR",
    "DT_AWARD",
    "TYPE_OF_CONTRACT",
    "CPV",
    "ISO_COUNTRY_CODE",    # buyer country
    "WIN_COUNTRY_CODE",    # supplier country
    "AWARD_VALUE_EURO",    # contract value
    "VALUE_EURO",          # estimated value (fallback)
    "CAE_TYPE",            # contracting authority type
    "MAIN_ACTIVITY",       # sector
    "TITLE",               # contract title
    "WIN_NAME",            # winner name
    "NUMBER_OFFERS",       # number of bids received
    "B_CONTRACTOR_SME",    # SME flag
]

print("Loading data (this may take a minute)...")
CHUNK_SIZE = 100_000
OUT_CSV = Path(
    r"C:\Users\Joe\Desktop\application\Job Application\project-for-applications\inverto-project\data\ted_clean.csv"
)
OUT_PARQUET = Path(
    r"C:\Users\Joe\Desktop\application\Job Application\project-for-applications\inverto-project\data\ted_clean.parquet"
)


def parse_award_dates(date_series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(
        date_series,
        format="%d/%m/%y",
        dayfirst=True,
        errors="coerce",
    )

    # Two-digit years can roll into the future (e.g., 68 -> 2068).
    current_year = pd.Timestamp.today().year
    future_mask = parsed.notna() & (parsed.dt.year > (current_year + 1))
    parsed.loc[future_mask] = parsed.loc[future_mask] - pd.DateOffset(years=100)
    return parsed


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    chunk["AWARD_VALUE_EURO"] = pd.to_numeric(chunk["AWARD_VALUE_EURO"], errors="coerce")
    chunk["VALUE_EURO"] = pd.to_numeric(chunk["VALUE_EURO"], errors="coerce")
    chunk["NUMBER_OFFERS"] = pd.to_numeric(chunk["NUMBER_OFFERS"], errors="coerce")

    chunk["DT_AWARD"] = parse_award_dates(chunk["DT_AWARD"])

    chunk = chunk.dropna(subset=["AWARD_VALUE_EURO", "DT_AWARD"])
    return chunk[chunk["AWARD_VALUE_EURO"] > 0]


def process_to_clean_csv() -> tuple[int, pd.Timestamp, pd.Timestamp, int, list[str], pd.Series]:
    if OUT_CSV.exists():
        OUT_CSV.unlink()

    total_rows = 0
    min_date = pd.NaT
    max_date = pd.NaT
    buyer_countries = set()
    contract_types = set()
    award_values = []

    # Prefer Arrow streaming to avoid pandas C-parser edge-case failures on very large files.
    def iter_source_chunks():
        try:
            import pyarrow.csv as pacsv

            reader = pacsv.open_csv(
                FILE,
                read_options=pacsv.ReadOptions(block_size=8 << 20),
                convert_options=pacsv.ConvertOptions(include_columns=COLS),
            )
            for batch in reader:
                yield batch.to_pandas(types_mapper=None)
        except Exception:
            # Fallback path if Arrow is unavailable or parsing fails unexpectedly.
            read_kwargs = {
                "usecols": COLS,
                "chunksize": CHUNK_SIZE,
                "engine": "python",
                "on_bad_lines": "skip",
            }
            for chunk in pd.read_csv(FILE, **read_kwargs):
                yield chunk

    for i, chunk in enumerate(iter_source_chunks(), start=1):
        cleaned = clean_chunk(chunk)

        if not cleaned.empty:
            total_rows += len(cleaned)

            chunk_min = cleaned["DT_AWARD"].min()
            chunk_max = cleaned["DT_AWARD"].max()
            min_date = chunk_min if pd.isna(min_date) else min(min_date, chunk_min)
            max_date = chunk_max if pd.isna(max_date) else max(max_date, chunk_max)

            buyer_countries.update(cleaned["ISO_COUNTRY_CODE"].dropna().astype(str).unique())
            contract_types.update(cleaned["TYPE_OF_CONTRACT"].dropna().astype(str).unique())
            award_values.append(cleaned["AWARD_VALUE_EURO"])

            cleaned.to_csv(OUT_CSV, mode="a", header=not OUT_CSV.exists(), index=False)

        if i % 10 == 0:
            print(f"  processed chunk {i:,}...")

    if total_rows == 0:
        raise RuntimeError("No valid rows were loaded after filtering.")

    value_series = pd.concat(award_values, ignore_index=True) if award_values else pd.Series(dtype=float)

    return (
        total_rows,
        min_date,
        max_date,
        len(buyer_countries),
        sorted(contract_types),
        value_series,
    )


def csv_to_parquet_chunked() -> bool:
    try:
        import pyarrow as pa
        import pyarrow.csv as pacsv
        import pyarrow.parquet as pq
    except ImportError:
        print("\nSkipping parquet conversion: pyarrow is not installed.")
        print("Install with: .venv\\Scripts\\python.exe -m pip install pyarrow")
        return False

    if OUT_PARQUET.exists():
        OUT_PARQUET.unlink()

    writer = None
    rows = 0
    batches = 0

    try:
        reader = pacsv.open_csv(OUT_CSV, read_options=pacsv.ReadOptions(block_size=1 << 20))
        for batch in reader:
            batches += 1
            table = pa.Table.from_batches([batch])
            rows += batch.num_rows

            if writer is None:
                writer = pq.ParquetWriter(OUT_PARQUET, table.schema, compression="snappy")

            writer.write_table(table)

            if batches % 25 == 0:
                print(f"  parquet batches written: {batches} (rows: {rows:,})")
    finally:
        if writer is not None:
            writer.close()

    return True


loaded_rows, min_date, max_date, buyer_country_count, contract_types, award_values = process_to_clean_csv()

print(f"\nLoaded {loaded_rows:,} records")
print(f"Date range: {min_date.date()} → {max_date.date()}")
print(f"Countries (buyers): {buyer_country_count}")
print(f"Contract types: {contract_types}")
print(f"\nValue stats (EUR):")
print(award_values.describe().apply(lambda x: f"{x:,.0f}"))

print(f"\nSaved clean data to: {OUT_CSV}")

if csv_to_parquet_chunked():
    print(f"Saved parquet data to: {OUT_PARQUET}")