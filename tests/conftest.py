from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest


def _business_days(start: date, n: int) -> pl.Series:
    days = pl.date_range(start, start + timedelta(days=int(n * 1.6) + 10), interval="1d", eager=True)
    days = days.filter(days.dt.weekday() < 6)
    return days.head(n)


@pytest.fixture
def price_data_factory():
    """Factory for synthetic ^GSPC-like daily price data (business days only)."""

    def _make(n=40, start=date(2024, 1, 2), seed=0, unique_id="^GSPC"):
        ds = _business_days(start, n)
        rng = np.random.default_rng(seed)
        y = 100 + np.cumsum(rng.normal(0, 1, n))
        return pl.DataFrame({"ds": ds, "y": y, "unique_id": [unique_id] * n})

    return _make


@pytest.fixture
def price_data(price_data_factory):
    return price_data_factory()
