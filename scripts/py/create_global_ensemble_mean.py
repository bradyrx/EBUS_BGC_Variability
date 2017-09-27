"""
Create global ensemble mean.

Generates an ensemble mean output file (netCDF) over the full global with
temporal resolution from 1920-2015 given an input variable and output directory.

This is helpful if you want to just make one residual file from a given
simulation.

INPUT 1: Variable (string)
INPUT 2: Output directory (string)
"""
import sys
import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

def main():
    VAR = sys.argv[1]
    print("Creating ensemble mean for " + VAR + "...")
    filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' + VAR +
                '_monthly/reduced/')
    ds = xr.open_mfdataset(filepath + '*.nc', decode_times=True,
                           concat_dim='ensemble')
    print("Dataset loaded.")
    ds = ds[VAR]
    ds = ds.squeeze()
    ds['time'] = pd.date_range('1920-01', '2101-01', freq='M')
    ds = ds.sel(time=slice('1920-01', '2015-12'))
    ds = ds.to_dataset()
    ds = ds.mean(dim='ensemble')
    print("Saving to NetCDF...")
    OUT = sys.argv[2]
    if not os.path.exists(OUT):
        os.makedirs(OUT)
    filename = (OUT + VAR + '.global_ensemble_mean.192001-201512.nochunks.nc')
    ds.to_netcdf(filename)
    print("Process complete.")

if __name__ == '__main__':
    main()
