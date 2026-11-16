import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client(tmp_path_factory, monkeypatch_module=None):
    subprocess.run([sys.executable, "scripts/make_demo_data.py"], cwd=ROOT, check=True)
    import os
    os.environ["DATA_DIR"] = str(ROOT / "data")
    from importlib import reload
    import app.main as m
    reload(m)
    return TestClient(m.app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_datasets(client):
    r = client.get("/datasets").json()
    assert r[0]["name"] == "demo_sst.nc" and "analysed_sst" in r[0]["variables"]


def test_timeseries(client):
    r = client.get("/timeseries", params={"dataset": "demo_sst.nc", "variable": "analysed_sst",
                                          "lat": 39.1, "lon": 26.2,
                                          "start": "2001-01-01", "end": "2001-01-31"}).json()
    assert len(r["time"]) == 31 and len(r["values"]) == 31


def test_climatology_has_12_months(client):
    r = client.get("/climatology", params={"dataset": "demo_sst.nc", "variable": "analysed_sst",
                                           "lat": 39.0, "lon": 26.0}).json()
    assert r["month"] == list(range(1, 13))
    assert max(r["mean"]) - min(r["mean"]) > 10  # clear seasonal cycle


def test_unknown_dataset_404(client):
    assert client.get("/timeseries", params={"dataset": "nope.nc", "variable": "x",
                                             "lat": 0, "lon": 0}).status_code == 404


def test_path_traversal_rejected(client):
    assert client.get("/timeseries", params={"dataset": "../secret.nc", "variable": "x",
                                             "lat": 0, "lon": 0}).status_code == 422
