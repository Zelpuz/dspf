import polars as pl
import holidays
from statsforecast.models import AutoARIMA
from dateutil.relativedelta import relativedelta
from datetime import datetime


def make_forecast(
    data: pl.DataFrame, horizon: int, season_length: int = 5
) -> pl.DataFrame:
    # Make the forecast
    forecaster = AutoARIMA(season_length=season_length)
    forecaster.fit(y=data.select("y").to_series().to_numpy())
    forecast = forecaster.forecast(y=data.select("y").to_series().to_numpy(), h=horizon)
    forecast = pl.DataFrame({"y": forecast["mean"]})

    # Add trading day-aware dates to the forecast
    final_day = data.select(pl.col("ds").tail(1)).item()
    nyse_holidays = list(
        holidays.financial_holidays(
            "NYSE", years=[(final_day).year for x in range(-1, 5)]
        ).keys()
    )
    next_15_trading_days = (
        pl.DataFrame(
            pl.date_range(
                start=final_day,
                end=final_day + relativedelta(days=30),
                interval="1d",
                closed="right",
                eager=True,
            ).alias("ds")
        )
        .filter(
            pl.col("ds").is_in(nyse_holidays).not_() & pl.col("ds").dt.is_business_day()
        )
        .select(pl.col("ds").head(15))
    )
    forecast = forecast.with_columns(next_15_trading_days.select("ds")).with_columns(
        pl.lit("^GSPC").alias("unique_id")
    )

    # vstack the forecast to the input data
    data = data.with_columns(pl.lit("historic").alias("type")).select(
        "ds", "y", "unique_id", "type"
    )
    forecast = forecast.with_columns(pl.lit("forecast").alias("type")).select(
        "ds", "y", "unique_id", "type"
    )
    data = data.vstack(forecast)

    return data


def forecast_from_today(
    data: pl.DataFrame, horizon: int, season_length: int = 5
) -> pl.DataFrame:
    today = datetime.today()
    data = data.filter((pl.col("ds") > (today - relativedelta(years=5))))
    forecast = make_forecast(data=data, horizon=horizon, season_length=season_length)
    return forecast
