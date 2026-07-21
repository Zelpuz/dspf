from types import SimpleNamespace

import polars as pl

import main as main_mod


def test_main_forecast_from_today_writes_csv(monkeypatch, tmp_path, capsys):
    fake_data = pl.DataFrame({"ds": [], "y": [], "unique_id": []})
    fake_forecast = pl.DataFrame(
        {"ds": ["2024-01-01"], "y": [1.0], "unique_id": ["^GSPC"], "type": ["forecast"]}
    )

    monkeypatch.setattr(main_mod, "download", lambda: fake_data)
    monkeypatch.setattr(
        main_mod, "forecast_from_today", lambda data, horizon: fake_forecast
    )
    monkeypatch.chdir(tmp_path)

    main_mod.main(SimpleNamespace(historic=False, progress_bar=False))

    assert capsys.readouterr().out == fake_forecast.write_csv()


def test_main_historic_flag_dispatches_to_historic_forecasts(
    monkeypatch, tmp_path, capsys
):
    fake_data = pl.DataFrame({"ds": [], "y": [], "unique_id": []})
    fake_forecast = pl.DataFrame(
        {"ds": [], "y": [], "unique_id": [], "type": [], "vintage": []}
    )
    called_with = {}

    def fake_historic_forecasts(args, data, horizon):
        called_with["args"] = args
        called_with["horizon"] = horizon
        return fake_forecast

    monkeypatch.setattr(main_mod, "download", lambda: fake_data)
    monkeypatch.setattr(main_mod, "historic_forecasts", fake_historic_forecasts)
    monkeypatch.chdir(tmp_path)

    args = SimpleNamespace(historic=True, progress_bar=True)
    main_mod.main(args)

    assert called_with["args"] is args
    assert called_with["horizon"] == 15
    assert capsys.readouterr().out == fake_forecast.write_csv()
