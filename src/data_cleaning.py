from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "fred_monthly_merged.csv"

SOURCE_CONFIG = {
    "cpi": {
        "file_name": "cpi.csv",
        "raw_column": "CPIAUCSL",
        "series_name": "cpi",
        "frequency": "monthly",
    },
    "fedfunds": {
        "file_name": "fedfunds.csv",
        "raw_column": "FEDFUNDS",
        "series_name": "fedfunds",
        "frequency": "monthly",
    },
    "sp500": {
        "file_name": "sp500.csv",
        "raw_column": "SP500",
        "series_name": "sp500",
        "frequency": "daily",
    },
    "vix": {
        "file_name": "vix.csv",
        "raw_column": "VIXCLS",
        "series_name": "vix",
        "frequency": "daily",
    },
}


def _check_input_files():
    missing_files = []
    for config in SOURCE_CONFIG.values():
        path = DATA_DIR / config["file_name"]
        if not path.exists():
            missing_files.append(str(path))
    if missing_files:
        raise FileNotFoundError(
            "Missing input data files:\n" + "\n".join(missing_files)
        )


def _read_series(config):
    file_path = DATA_DIR / config["file_name"]
    df = pd.read_csv(file_path, parse_dates=["observation_date"])
    if "observation_date" not in df.columns:
        raise ValueError(f"Expected observation_date column in {file_path}")

    if config["raw_column"] not in df.columns:
        raise ValueError(
            f"Expected {config['raw_column']} column in {file_path}, got {list(df.columns)}"
        )

    df = df.rename(
        columns={
            "observation_date": "date",
            config["raw_column"]: config["series_name"],
        }
    )
    df = df[["date", config["series_name"]]].copy()
    df[config["series_name"]] = pd.to_numeric(
        df[config["series_name"]], errors="coerce"
    )
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.set_index("date")

    if config["frequency"] == "daily":
        # For daily market series we carry forward the last observed close through calendar days
        # so the month-end aggregation captures the real last trading-day value.
        series = df[config["series_name"]].resample("D").last().ffill()
        return series.resample("ME").last()

    return df[config["series_name"]].resample("ME").last().ffill()


def _categorize_rate_regime(rate_change):
    if pd.isna(rate_change):
        return "flat"
    if rate_change > 0:
        return "rising"
    if rate_change < 0:
        return "falling"
    return "flat"


def _categorize_volatility(vix_value: float) -> str:
    if pd.isna(vix_value):
        return "unknown"
    if vix_value < 18:
        return "low"
    if vix_value < 25:
        return "medium"
    return "high"


def build_clean_dataset() -> pd.DataFrame:
    _check_input_files()

    series_frames = []
    for config in SOURCE_CONFIG.values():
        series = _read_series(config)
        series_frames.append(series)

    merged = pd.concat(series_frames, axis=1, join="outer").sort_index()
    merged = merged.dropna(subset=["sp500", "vix", "cpi", "fedfunds"])

    merged["year"] = merged.index.year
    merged["month"] = merged.index.month
    merged["sp500_pct_change"] = merged["sp500"].pct_change()
    merged["inflation_pct_change"] = merged["cpi"].pct_change(periods=12)
    merged["rate_change"] = merged["fedfunds"].diff()
    merged["rate_regime"] = merged["rate_change"].apply(_categorize_rate_regime)
    merged["volatility_regime"] = merged["vix"].apply(_categorize_volatility)

    merged = merged.reset_index()
    merged.to_csv(OUTPUT_CSV, index=False, float_format="%.6f")
    return merged


def main():
    print("Building cleaned monthly dataset from FRED source files...")
    clean_df = build_clean_dataset()
    print(f"Saved cleaned dataset to {OUTPUT_CSV}")
    print("Rows in cleaned dataset:", len(clean_df))


if __name__ == "__main__":
    main()
