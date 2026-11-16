"""Small FastAPI service that serves point time series and monthly
climatologies from local NetCDF files (e.g. CMEMS SST, ERA5 fields).

Run:  uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
import os
from pathlib import Path

import numpy as np
import xarray as xr
from fastapi import FastAPI, HTTPException, Query

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))

app = FastAPI(title="Marine data API", version="0.1.0")

LAT_NAMES = ("latitude", "lat")
LON_NAMES = ("longitude", "lon")
TIME_NAMES = ("time", "valid_time")


def _find(ds: xr.Dataset, names) -> str:
    for n in names:
        if n in ds.coords or n in ds.dims:
            return n
    raise HTTPException(500, f"None of {names} found in dataset coordinates")


def _open(name: str) -> xr.Dataset:
    # Only plain file names inside DATA_DIR are allowed (no path traversal).
    if Path(name).name != name or not name.endswith(".nc"):
        raise HTTPException(422, "dataset must be a plain .nc file name")
    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(404, f"dataset '{name}' not found")
    return xr.open_dataset(path)


def _point_series(name, variable, lat, lon, start, end) -> xr.DataArray:
    ds = _open(name)
    if variable not in ds.data_vars:
        raise HTTPException(404, f"variable '{variable}' not in {name}; "
                                 f"available: {list(ds.data_vars)}")
    la, lo, t = _find(ds, LAT_NAMES), _find(ds, LON_NAMES), _find(ds, TIME_NAMES)
    da = ds[variable].sel({la: lat, lo: lon}, method="nearest")
    if start or end:
        da = da.sel({t: slice(start, end)})
    if da.sizes[t] == 0:
        raise HTTPException(404, "no data in requested time range")
    return da.rename({t: "time"}) if t != "time" else da


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datasets")
def list_datasets():
    """List NetCDF files in DATA_DIR with variables and time coverage."""
    out = []
    for p in sorted(DATA_DIR.glob("*.nc")):
        with xr.open_dataset(p) as ds:
            t = _find(ds, TIME_NAMES)
            out.append({
                "name": p.name,
                "variables": list(ds.data_vars),
                "time_start": str(ds[t].values.min())[:10],
                "time_end": str(ds[t].values.max())[:10],
            })
    return out


@app.get("/timeseries")
def timeseries(
    dataset: str,
    variable: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=360),
    start: str | None = None,
    end: str | None = None,
):
    """Time series at the grid point nearest to (lat, lon)."""
    da = _point_series(dataset, variable, lat, lon, start, end)
    return {
        "dataset": dataset,
        "variable": variable,
        "grid_lat": float(da[_find(da.to_dataset(name="v"), LAT_NAMES)]),
        "grid_lon": float(da[_find(da.to_dataset(name="v"), LON_NAMES)]),
        "time": [str(v)[:10] for v in da["time"].values],
        "values": [None if np.isnan(v) else float(v) for v in da.values],
    }


@app.get("/climatology")
def climatology(
    dataset: str,
    variable: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=360),
    start: str | None = None,
    end: str | None = None,
):
    """Mean seasonal cycle (12 monthly means) at the nearest grid point."""
    da = _point_series(dataset, variable, lat, lon, start, end)
    monthly = da.groupby("time.month").mean(skipna=True)
    return {
        "dataset": dataset,
        "variable": variable,
        "month": [int(m) for m in monthly["month"].values],
        "mean": [None if np.isnan(v) else float(v) for v in monthly.values],
    }
