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
    ds['time']  = pd.date_range('1920-01', '2101-01', freq='M')
    # Extract 1920-2015
    ds = ds.sel(time=slice('1920-01','2015-12'))
    # Find ensemble mean
    ds = ds.mean(dim='ensemble')
    print("Computing seasonal magnitude across grid...")
    s_magnitude = ds.stack(allpoints=['nlat','nlon']) \
                    .groupby('allpoints', squeeze=False) \
                    .apply(et.ufunc.seasonal_magnitude) \
                    .unstack('allpoints')
    s_magnitude.name = 's_magnitude'
    s_magnitude.attrs['long name'] = 'Magnitude of 1920-2015 seasonal cycle'
    # To save memory...
    del ds
    
    # Find residuals
    ds = load_ensemble(VAR)
    ds = ds.sel(time=slice('1920-01', '2015-12'))
    ds = ds - ds.mean(dim='ensemble')
    ds = ds[VAR].std(dim='time').mean(dim='ensemble')
    ds.name = 'r_magnitude'
    ds.attrs['long name'] = 'Mean standard deviation of 1920-2015 residuals'

    # Create new dataset for storage and saving
    variability = xr.Dataset()
    variability['s_magnitude'] = s_magnitude
    variability['r_magnitude'] = ds
    del ds
    variability.to_netcdf('/glade/scratch/rbrady/EBUS_BGC_Variability/' + 
                          'global_' + VAR + '_variability_test.nc')

if __name__ == '__main__':
    main()

