import pandas as pd
import polars as pl

import data_pipe


class FakeTicker:
    """Stands in for yfinance's Ticker so tests don't hit the network."""

    last_symbol = None
    last_period = None
    history_df = None

    def __init__(self, symbol):
        FakeTicker.last_symbol = symbol

    def history(self, period):
        FakeTicker.last_period = period
        return FakeTicker.history_df


def test_download_requests_the_right_symbol_and_period(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=3, freq="D", name="Date")
    FakeTicker.history_df = pd.DataFrame({"Close": [1.0, 2.0, 3.0]}, index=idx)
    monkeypatch.setattr(data_pipe.yf, "Ticker", FakeTicker)

    data_pipe.download()

    assert FakeTicker.last_symbol == "^GSPC"
    assert FakeTicker.last_period == "10y"


def test_download_shapes_output_dataframe(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=5, freq="D", name="Date")
    # Real yfinance history() returns extra columns; download() should drop them.
    FakeTicker.history_df = pd.DataFrame(
        {
            "Open": [0.0] * 5,
            "Close": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Volume": [100] * 5,
        },
        index=idx,
    )
    monkeypatch.setattr(data_pipe.yf, "Ticker", FakeTicker)

    result = data_pipe.download()

    assert result.columns == ["ds", "y", "unique_id"]
    assert result.schema["ds"] == pl.Date
    assert result["y"].to_list() == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert result["unique_id"].to_list() == ["^GSPC"] * 5
    assert result["ds"].to_list() == [d.date() for d in idx.to_pydatetime()]
