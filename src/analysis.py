from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
CHART_DIR = OUTPUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "finance_project.db"
SQL_FILE = ROOT_DIR / "sql" / "analysis_queries.sql"


def _connect_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database file not found. Run src/database_build.py first: {DB_PATH}"
        )
    return sqlite3.connect(DB_PATH)


def _load_query_text():
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")
    return SQL_FILE.read_text(encoding="utf-8")


def _parse_queries(sql_text):
    queries = []
    current = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if not stripped:
            continue
        current.append(line)
        if stripped.endswith(";"):
            queries.append("\n".join(current).rstrip("; "))
            current = []
    if current:
        queries.append("\n".join(current))
    return queries


def execute_queries():
    sql_text = _load_query_text()
    queries = _parse_queries(sql_text)
    failed_queries = []

    print("Executing SQL queries from", SQL_FILE)
    with _connect_db() as conn:
        for idx, query in enumerate(queries, start=1):
            try:
                df = pd.read_sql_query(query, conn)
                print(f"\nQuery {idx} result (first 10 rows):")
                print(df.head(10).to_string(index=False))
            except Exception as exc:
                failed_queries.append(idx)
                print(f"Failed to execute query {idx}: {exc}")

    if failed_queries:
        raise RuntimeError(f"Failed SQL queries: {failed_queries}")


def _plot_line(x, y, title, output_name, xlabel="Date", ylabel="Value"):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, color="tab:blue", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    output_path = CHART_DIR / output_name
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def _plot_scatter(x, y, title, output_name, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, color="tab:purple", alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    output_path = CHART_DIR / output_name
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def _plot_bar(categories, values, title, output_name, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(categories, values, color="tab:green", edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    output_path = CHART_DIR / output_name
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def build_charts():
    with _connect_db() as conn:
        df = pd.read_sql_query("SELECT * FROM fred_monthly_data ORDER BY date", conn)

    df["date"] = pd.to_datetime(df["date"])

    _plot_line(
        df["date"],
        df["sp500"],
        "S&P 500 Monthly Close",
        "sp500_over_time.png",
        ylabel="S&P 500",
    )
    _plot_line(
        df["date"],
        df["fedfunds"],
        "Federal Funds Rate",
        "fedfunds_over_time.png",
        ylabel="Fed Funds Rate",
    )
    _plot_line(
        df["date"],
        df["cpi"],
        "Consumer Price Index (CPI)",
        "cpi_over_time.png",
        ylabel="CPI",
    )
    _plot_line(df["date"], df["vix"], "VIX Monthly Close", "vix_over_time.png", ylabel="VIX")
    _plot_scatter(
        df["fedfunds"],
        df["sp500_pct_change"],
        "S&P 500 Monthly Returns vs Fed Funds Rate",
        "sp500_vs_fedfunds.png",
        xlabel="Fed Funds Rate",
        ylabel="S&P 500 Monthly Return",
    )
    _plot_scatter(
        df["inflation_pct_change"],
        df["sp500_pct_change"],
        "S&P 500 Monthly Returns vs Inflation (YoY)",
        "sp500_vs_inflation.png",
        xlabel="Inflation YoY Change",
        ylabel="S&P 500 Monthly Return",
    )

    rate_summary = (
        df.groupby("rate_regime")["sp500_pct_change"]
        .mean()
        .reindex(["rising", "falling", "flat"])
    )
    _plot_bar(
        rate_summary.index.astype(str),
        rate_summary.values,
        "Average S&P 500 Return by Rate Regime",
        "avg_return_by_rate_regime.png",
        xlabel="Rate Regime",
        ylabel="Average Monthly Return",
    )

    volatility_summary = (
        df.groupby("volatility_regime")["sp500_pct_change"]
        .mean()
        .reindex(["low", "medium", "high"])
    )
    _plot_bar(
        volatility_summary.index.astype(str),
        volatility_summary.values,
        "Average S&P 500 Return by Volatility Regime",
        "avg_return_by_volatility_regime.png",
        xlabel="Volatility Regime",
        ylabel="Average Monthly Return",
    )


def main():
    print("Running SQL queries and building charts...")
    execute_queries()
    build_charts()


if __name__ == "__main__":
    main()
