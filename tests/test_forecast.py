import polars as pl
import pytest

import forecast as forecast_mod
from forecast import (
    _make_historic_forecast,
    forecast_from_today,
    historic_forecasts,
    make_forecast,
)


class Args:
    def __init__(self, progress_bar=False):
        self.progress_bar = progress_bar


# --- make_forecast ---------------------------------------------------------


def test_make_forecast_returns_requested_horizon(price_data_factory):
    data = price_data_factory(n=40)
    result = make_forecast(data, horizon=5)
    assert result.height == 5


def test_make_forecast_schema(price_data_factory):
    data = price_data_factory(n=40)
    result = make_forecast(data, horizon=5)
    assert result.columns == ["ds", "y", "unique_id", "type"]
    assert result["type"].unique().to_list() == ["forecast"]
    assert result["unique_id"].unique().to_list() == ["^GSPC"]


def test_make_forecast_dates_are_future_business_days(price_data_factory):
    data = price_data_factory(n=40)
    last_input_day = data["ds"].max()

    result = make_forecast(data, horizon=5)

    ds = result["ds"].to_list()
    assert min(ds) > last_input_day
    assert ds == sorted(ds)
    assert all(d.weekday() < 5 for d in ds)  # Mon-Fri only


# --- forecast_from_today ----------------------------------------------------


def test_forecast_from_today_appends_forecast_to_history(price_data_factory):
    data = price_data_factory(n=60)

    result = forecast_from_today(data=data, horizon=5)

    assert set(result["type"].unique().to_list()) == {"historic", "forecast"}
    assert result.filter(pl.col("type") == "forecast").height == 5
    assert result.filter(pl.col("type") == "historic").height == data.height


# --- historic forecasting: no peeking into the future -----------------------


def test_make_historic_forecast_ignores_data_after_start_date(price_data_factory):
    """A vintage forecast must only depend on data up to and including start_date.

    We build two datasets that are identical up to a cutoff and diverge wildly
    after it, then confirm the forecast produced *as of* that cutoff is
    unaffected by the divergence (per the "no peeking" claim in the README).
    """
    data = price_data_factory(n=40)
    start_date = data["ds"][20]

    tampered = data.with_columns(
        pl.when(pl.col("ds") > start_date)
        .then(pl.col("y") * 100)
        .otherwise(pl.col("y"))
        .alias("y")
    )

    baseline = _make_historic_forecast(start_date, data=data, horizon=3, season_length=5)
    tampered_result = _make_historic_forecast(
        start_date, data=tampered, horizon=3, season_length=5
    )

    assert baseline["y"].to_list() == tampered_result["y"].to_list()


def test_make_historic_forecast_tags_vintage(price_data_factory):
    data = price_data_factory(n=40)
    start_date = data["ds"][20]

    result = _make_historic_forecast(start_date, data=data, horizon=3, season_length=5)

    assert result["vintage"].unique().to_list() == [start_date]


# --- historic_forecasts orchestration (fitting itself is mocked out) --------


@pytest.mark.parametrize("progress_bar", [False, True])
def test_historic_forecasts_calls_once_per_vintage_and_concatenates(
    monkeypatch, price_data_factory, progress_bar
):
    data = price_data_factory(n=8)

    # joblib.Parallel runs this in worker processes, so it can only report
    # what happened via its return value -- not via a shared-memory side effect.
    def fake_make_historic_forecast(start_date, data, horizon, season_length):
        return pl.DataFrame(
            {
                "ds": [start_date],
                "y": [1.0],
                "unique_id": ["^GSPC"],
                "type": ["forecast"],
                "vintage": [start_date],
            }
        )

    monkeypatch.setattr(forecast_mod, "_make_historic_forecast", fake_make_historic_forecast)

    result = historic_forecasts(
        args=Args(progress_bar=progress_bar), data=data, horizon=2, season_length=5
    )

    assert sorted(result["vintage"].to_list()) == sorted(data["ds"].to_list())
    assert result.height == data.height
    assert result["vintage"].n_unique() == data.height
