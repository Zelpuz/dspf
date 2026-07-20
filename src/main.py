import argparse, os
from pathlib import Path
from data_pipe import download, save_to_file
from forecast import make_forecast


def main():
    data = download()
    forecast = make_forecast(data=data, horizon=15)

    path = Path(os.getcwd())
    (path / "dspf_output").mkdir(parents=True, exist_ok=True)
    save_to_file(data=forecast, path=path / "dspf_output")


if __name__ == "__main__":
    main()
