# DSPF: Daily S&P500 forecaster

This app, DSPF, generates a forecast of daily closing prices for the S&P500 as listed on the NYSE. Upon execution DSPF downloads the last five years' daily closing prices and then forecasts closing prices for the next 15 trading days, or approximately three weeks.

DSPF also reports metrics for historic forecasts. Users can see both current forecasts and assess past forecast strength.

## Methodology

Forecasts are generated using an AutoARIMA procedure. Non-trading days are removed and trading days are treated as adjacent time steps.

As the AutoARIMA procedure is effectively deterministic, that is, you get the same result upon rerunning with the same data, we do not need to store forecasts for future evaluation. Instead, the app generates historic forecasts each time it is run and uses those to assess historic accuracy. These historic forecasts do not _peek_; only data up to and including a trading day is used to predict subsequent trading days' closing prices.

Despite not needing saved forecasts for evaluation, DSPF exports historic and current forecasts as a CSV for users' convenience.

## Code

This app uses Python. Key third-party packages include `polars` and `statsforecast`. Trading holidays are tracked with `holidays`.

