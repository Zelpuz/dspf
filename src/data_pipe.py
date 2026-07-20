import polars as pl
import yfinance as yf
from pathlib import Path


def download() -> pl.DataFrame:
    data = (
        pl.from_pandas(yf.Ticker("^GSPC").history("10y").reset_index())
        .cast({"Date": pl.Date})
        .select(
            pl.col("Date").alias("ds"),
            pl.col("Close").alias("y"),
            pl.lit("^GSPC").alias("unique_id"),
        )
    )

    return data