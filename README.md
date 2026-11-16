# marine-data-api

A small FastAPI service for working with gridded ocean and atmosphere data
(NetCDF), in the style of CMEMS SST and ERA5 fields. It serves point time
series and mean seasonal cycles from local files, and includes download
scripts for Copernicus Marine and the Copernicus Climate Data Store.

This is a compact example project, not a full production system.

## Endpoints

| Endpoint | What it returns |
|---|---|
| `GET /health` | service status |
| `GET /datasets` | NetCDF files in `data/`, with variables and time coverage |
| `GET /timeseries` | time series at the grid point nearest to `lat`, `lon` |
| `GET /climatology` | 12-month mean seasonal cycle at the nearest grid point |

Interactive docs are available at `/docs` when the server is running.

## Quick start

```bash
pip install -r requirements.txt
python scripts/make_demo_data.py      # synthetic demo file, no download needed
uvicorn app.main:app --reload
```

Example request:

```
http://127.0.0.1:8000/climatology?dataset=demo_sst.nc&variable=analysed_sst&lat=39&lon=26
```

## Using real data

```bash
copernicusmarine login                 # once; credentials stay in your home directory
python scripts/download_cmems_sst.py --start 1982-01-01 --end 2025-12-31
python scripts/download_era5.py --year 2020   # needs ~/.cdsapirc
```

Check the Copernicus Marine dataset id in the catalogue before use, because
product ids and versions change. Credentials are never stored in this
repository (see `.gitignore`).

## Tests

```bash
pytest
```

## Notes

- Files are read from `data/` (override with the `DATA_DIR` environment variable).
- Only plain `.nc` file names are accepted, so paths outside `data/` cannot be requested.
- Handles `latitude`/`lat`, `longitude`/`lon` and `time`/`valid_time` coordinate names.
