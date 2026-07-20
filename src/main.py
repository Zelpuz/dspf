import argparse, os, sys
from pathlib import Path
from data_pipe import download
from forecast import forecast_from_today


def main():
    data = download()
    forecast = forecast_from_today(data=data, horizon=15)

    path = Path(os.getcwd())
    (path / "dspf_output").mkdir(parents=True, exist_ok=True)
    sys.stdout.write(data.write_csv())


if __name__ == "__main__":
    main()
