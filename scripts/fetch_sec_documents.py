import argparse
from pathlib import Path
from research_rag.documents import fetch_sec

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NVDA", "JPM", "GS"],
    )
    parser.add_argument(
        "--forms",
        nargs="+",
        default=["10-K", "10-Q"],
    )
    parser.add_argument("--per-form", type=int, default=1)
    args = parser.parse_args()

    count = fetch_sec(
        args.tickers,
        args.forms,
        args.per_form,
        Path("data/raw/sec"),
    )
    print(f"Downloaded {count} SEC filings")
