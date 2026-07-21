import sys
import argparse
from data_pipe import download
from forecast import forecast_from_today, historic_forecasts


def main(args):
    data = download()

    if args.historic:
        forecast = historic_forecasts(args=args, data=data, horizon=15)
    else:
        forecast = forecast_from_today(data=data, horizon=15)

    sys.stdout.write(forecast.write_csv())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="dspf",
        description="S&P500 forecaster",
    )
    parser.add_argument("--historic", action="store_true")
    parser.add_argument("--progress_bar", action="store_true")
    args = parser.parse_args()
    main(args)
