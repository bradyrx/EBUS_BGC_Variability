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
        if (VAR == "FG_CO2") or (VAR == "FG_ALT_CO2"):
            # Convert to intelligible units.
            ds[VAR] = ds[VAR] * ((-1 * 3600 * 24 * 365.25) / (1000 * 100))
        return ds

def main():
    VAR = sys.argv[1]
    ds = load_ensemble(VAR)
    # Extract 1920-2015
    ds = ds.sel(time=slice('1920-01','2015-12'))
    # Find ensemble mean
    ds = ds.mean(dim='ensemble')
    # Save out and load back in
    temp_file = '/glade/scratch/rbrady/temp_' + VAR + '.nc'
    ds.to_netcdf(temp_file)
    del ds
    ds = xr.open_dataset(temp_file)
    print("Computing seasonal magnitude across grid...")
    ds = ds[VAR].stack(allpoints=['nlat','nlon']) \
                    .groupby('allpoints', squeeze=False) \
                    .apply(et.ufunc.seasonal_magnitude) \
                    .unstack('allpoints')
    ds.name = 's_magnitude'
    ds.attrs['long name'] = 'Magnitude of 1920-2015 seasonal cycle'
    # Save as temporary netCDF for memory concerns.
    seasonal_file = '/glade/scratch/rbrady/seasonal_' + VAR + '.nc'
    ds.to_dataset().to_netcdf(seasonal_file)
    # To save memory...
    del ds
    os.remove(temp_file)
    # Find residuals
    print("Computing residuals across grid...")
    ds = load_ensemble(VAR)
    ds = ds.sel(time=slice('1920-01', '2015-12'))
    ds = ds - ds.mean(dim='ensemble')
    ds = ds[VAR].std(dim='time').mean(dim='ensemble')
    ds.name = 'r_magnitude'
    ds.attrs['long name'] = 'Mean standard deviation of 1920-2015 residuals'
    ds = ds.to_dataset()
    # Load back in seasonal file.
    ds2 = xr.open_dataset(seasonal_file)
    os.remove(seasonal_file)
    variability = xr.Dataset()
    variability['s_magnitude'] = ds2['s_magnitude']
    variability['r_magnitude'] = ds['r_magnitude']
    # Add in global coordinates for reference.
    coords = xr.open_dataset('/glade/p/work/rbrady/EBUS_BGC_Variability/' + 
                             'global_coordinates.nc')
    variability.coords['TLAT'] = coords['TLAT']
    variability['TAREA'] = coords['TAREA']
    # Save out!
    directory = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR +
                 '/global/')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = VAR + '_seasonal_internal_global_magnitudes.nc'
    variability.to_netcdf(directory + filename)
    print("End task.")

if __name__ == '__main__':
    main()

