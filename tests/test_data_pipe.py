import pandas as pd
import polars as pl

import data_pipe


def _install_fake_ticker(monkeypatch, history_df):
    """Stands in for yfinance's Ticker so tests don't hit the network.

    Returns the list of (symbol, period) pairs `.history()` was called with.
    """
    calls = []

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, period):
            calls.append((self.symbol, period))
            return history_df

    monkeypatch.setattr(data_pipe.yf, "Ticker", FakeTicker)
    return calls


def test_download_requests_the_right_symbol_and_period(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=3, freq="D", name="Date")
    history_df = pd.DataFrame({"Close": [1.0, 2.0, 3.0]}, index=idx)
    calls = _install_fake_ticker(monkeypatch, history_df)

    data_pipe.download()

    assert calls == [("^GSPC", "10y")]


def test_download_shapes_output_dataframe(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=5, freq="D", name="Date")
    # Real yfinance history() returns extra columns; download() should drop them.
    history_df = pd.DataFrame(
        {
            "Open": [0.0] * 5,
            "Close": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Volume": [100] * 5,
        },
        index=idx,
    )
    _install_fake_ticker(monkeypatch, history_df)

    result = data_pipe.download()

    assert result.columns == ["ds", "y", "unique_id"]
    assert result.schema["ds"] == pl.Date
    assert result["y"].to_list() == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert result["unique_id"].to_list() == ["^GSPC"] * 5
    assert result["ds"].to_list() == [d.date() for d in idx.to_pydatetime()]
