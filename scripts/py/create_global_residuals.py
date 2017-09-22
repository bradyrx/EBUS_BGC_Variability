"""
Create global residuals.

Given an INPUT variable, this script grabs the full raw global ensemble and 
generates an OUTPUT .nc file full of the residuals. It removes the ensemble
mean and saves residuals with time labeling from 1920-2015.

INPUT 1 : Variable (string)
INPUT 2 : Output directory (string)
"""
import sys
import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

ens = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
       '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
       '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
       '102', '103', '104', '105']

def main():
    VAR = sys.argv[1]
    print("Creating global residuals for "  + VAR + "...")
    fileDir = '/glade/scratch/rbrady/EBUS_BGC_Variability/' + VAR + '_monthly/'
    ds = xr.open_mfdataset(fileDir + '*.nc', decode_times=False,
                           concat_dim='ensemble', chunks={'time':10})
    print("Dataset loaded.")
    ds = ds[VAR]
    ds = ds.squeeze()
    ds = ds - ds.mean(dim='ensemble')
    ds['time'] = pd.date_range('1920-01', '2101-01', freq='M')
    ds = ds.sel(time=slice('1920-01','2015-12'))
    print("Globe subsetted.")
    OUTPUT = sys.argv[2]
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    print("Saving to netCDF...")
    for i in range(ds.shape[0]):
        filename = (OUTPUT + VAR + '.' + ens[i] + '.global_residuals.nc')
        ds[i].to_dataset().to_netcdf(filename)
        print("Saving ensemble number " + ens[i] + "...")
    print("Process complete.")

if __name__ == '__main__':
    main()
