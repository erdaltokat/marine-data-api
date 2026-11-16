"""Download a daily SST subset from Copernicus Marine.

Credentials: run `copernicusmarine login` once (stored in your home
directory). Do NOT put a username/password in this file.

Check the dataset id in the Copernicus Marine catalogue before use;
product ids and versions change over time.
"""
import argparse
import copernicusmarine

p = argparse.ArgumentParser()
p.add_argument("--dataset-id", default="cmems_obs-sst_glo_phy_my_l4_P1D-m")
p.add_argument("--variable", default="analysed_sst")
p.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"),
               default=[25.0, 38.0, 28.0, 41.0])
p.add_argument("--start", default="2000-01-01")
p.add_argument("--end", default="2004-12-31")
p.add_argument("--out", default="data/cmems_sst.nc")
a = p.parse_args()

copernicusmarine.subset(
    dataset_id=a.dataset_id,
    variables=[a.variable],
    minimum_longitude=a.bbox[0], minimum_latitude=a.bbox[1],
    maximum_longitude=a.bbox[2], maximum_latitude=a.bbox[3],
    start_datetime=a.start, end_datetime=a.end,
    output_filename=a.out,
)
