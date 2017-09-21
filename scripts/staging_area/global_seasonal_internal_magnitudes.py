"""
GLOBAL SEASONAL/INTERNAL MAGNITUDES
Author : Riley X. Brady
Date : Sep. 20th, 2017
Purpose: Given an ocean variable, this will find the magnitude of the historical
seasonal cycle and the magnitude of internal variability over the global grid.
It will save each magnitude as a netCDF variable.
"""
# INPUT 1: Variable name (str)
import glob
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr
import esmtools as et

def load_ensemble(VAR):
        """
        Loads the global full ensemble from scratch space.
        """
        fileDir = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' +
                   VAR + '_monthly/')
        ds = xr.open_mfdataset(fileDir + 'reduced*.nc', decode_times=False,
                               concat_dim='ensemble', chunks={'time':10})
        ds.attrs = {}
        ds = ds[VAR].to_dataset()
        ds['time'] = pd.date_range('1920-01', '2101-01', freq='M')
        return ds

def main():
    VAR = sys.argv[1]
    ds = load_ensemble(VAR)
    # Extract 1920-2015
    ds = ds.sel(time=slice('1920-01','2015-12'))
    # Find ensemble mean
    ds = ds.mean(dim='ensemble')
    # Save out and load back in
    ds.to_netcdf('/glade/scratch/rbrady/temp.nc')
    del ds
    ds = xr.open_dataset('/glade/scratch/rbrady/temp.nc')
    print("Computing seasonal magnitude across grid...")
    ds = ds[VAR].stack(allpoints=['nlat','nlon']) \
                    .groupby('allpoints', squeeze=False) \
                    .apply(et.ufunc.seasonal_magnitude) \
                    .unstack('allpoints')
    ds.name = 's_magnitude'
    ds.attrs['long name'] = 'Magnitude of 1920-2015 seasonal cycle'
    ds.to_dataset().to_netcdf('/glade/scratch/rbrady/EBUS_BGC_Variability/' +
                              VAR + '_seasonal_magnitude_global.nc')
    # To save memory...
    del ds
    
    # Find residuals
    ds = load_ensemble(VAR)
    ds = ds.sel(time=slice('1920-01', '2015-12'))
    ds = ds - ds.mean(dim='ensemble')
    ds = ds[VAR].std(dim='time').mean(dim='ensemble')
    ds.name = 'r_magnitude'
    ds.attrs['long name'] = 'Mean standard deviation of 1920-2015 residuals'
    ds.to_dataset().to_netcdf('/glade/scratch/rbrady/EBUS_BGC_Variability/' +
                              VAR + '_internal_magnitude_global.nc')
    del ds
    print("End task.")

if __name__ == '__main__':
    main()

