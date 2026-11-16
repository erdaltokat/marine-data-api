"""Create a small synthetic NetCDF file so the API can be tried without
downloading anything. Values are artificial (seasonal cycle + noise)."""
import numpy as np
import pandas as pd
import xarray as xr

time = pd.date_range("2000-01-01", "2004-12-31", freq="D")
lat = np.arange(38.0, 41.01, 0.25)
lon = np.arange(25.0, 28.01, 0.25)
rng = np.random.default_rng(0)

doy = time.dayofyear.values
seasonal = 16 + 7 * np.sin(2 * np.pi * (doy - 110) / 365.25)
sst = seasonal[:, None, None] + rng.normal(0, 0.3, (len(time), len(lat), len(lon)))

ds = xr.Dataset(
    {"analysed_sst": (("time", "latitude", "longitude"), sst.astype("float32"),
                      {"units": "degC", "long_name": "synthetic SST"})},
    coords={"time": time, "latitude": lat, "longitude": lon},
)
ds.to_netcdf("data/demo_sst.nc")
print("wrote data/demo_sst.nc")
