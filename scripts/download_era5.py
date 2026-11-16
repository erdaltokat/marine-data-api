"""Download ERA5 single-level fields from the Copernicus Climate Data Store.

Credentials: create ~/.cdsapirc with your CDS API key as described in the
CDS documentation. Do NOT put the key in this file.
"""
import argparse
import cdsapi

p = argparse.ArgumentParser()
p.add_argument("--year", default="2020")
p.add_argument("--area", nargs=4, type=float, metavar=("N", "W", "S", "E"),
               default=[41.0, 25.0, 38.0, 28.0])
p.add_argument("--out", default="data/era5_2020.nc")
a = p.parse_args()

cdsapi.Client().retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "variable": ["2m_temperature", "10m_u_component_of_wind",
                     "10m_v_component_of_wind"],
        "year": a.year,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": ["00:00", "06:00", "12:00", "18:00"],
        "area": a.area,
        "data_format": "netcdf",
    },
    a.out,
)
