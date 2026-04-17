from pathlib import Path
import sqlite3
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
DB_PATH = OUTPUT_DIR / "finance_project.db"
CSV_PATH = OUTPUT_DIR / "fred_monthly_merged.csv"


def create_database():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned CSV file not found. Run src/data_cleaning.py first: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("fred_monthly_data", conn, if_exists="replace", index=False)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_fred_monthly_date ON fred_monthly_data(date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_fred_monthly_rate_regime ON fred_monthly_data(rate_regime)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_fred_monthly_volatility_regime ON fred_monthly_data(volatility_regime)"
        )
        conn.commit()

    print(f"SQLite database created at {DB_PATH}")


if __name__ == "__main__":
    create_database()
