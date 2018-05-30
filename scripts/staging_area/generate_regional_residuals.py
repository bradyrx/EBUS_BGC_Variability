# Author : Riley X. Brady
# Date   : June 30th, 2017
"""
Desc   : This script should be ran after running EBUS_Extraction.py. The
extraction script will take a .nc of a global surface field, and pull out the
four major EBUS, saving them as separate .nc files for analysis
(simulation-by-simulation). This script then draws in the full ensemble,
filtering by 10 degrees of latitude and 800km (or user input) offshore, also
subtracting out the ensemble mean to create residuals. It then saves the
ensemble residuals (34 x time) into one netCDF file. For stats analysis
scripts, you can then load in that ensemble netCDF of residuals and perform
quick analyses on this. This helps since so many functions are performed on
the ensemble residuals -- it speeds up that analysis in terms of not needing
to generate the residuals every time. It also physically speeds up analysis
by cleaning up the dask array. For whatever reason, xarray/dask is
SIGNIFICANTLY faster upon loading in post-processed .nc files.
"""
# ----------------------
# Update  : Sep 6th, 2017
# Recently moved over to Python3 from Python2. Simply updated the print portions
# of this script to make them compatible with print as a function.
# ----------------------
# Input 1 : EBU name.
# Input 2 : Variable name.
# NOTE: You can change the offshore distance parameter in the main script if
# needed. I didn't make it an input option, since 800km should be pretty
# standard for awhile.
# Load in packages.
import os
import sys
import glob
import numpy as np
import pandas as pd
import xarray as xr

def chavez_bounds(x):
    """
    Returns the appropriate 10 degree latitude bounds from the Chavez 2009 EBUS
    comparison paper. These are the bounds used for equal region comparisons
    across the EBUS.
    """
    if x == "CalCS":
        lat1 = 34
        lat2 = 44
    elif x == "CanCS":
        lat1 = 21 
        lat2 = 31 
    elif x == "BenCS":
        lat1 = -28
        lat2 = -18
    elif x == "HumCS":
        lat1 = -16
        lat2 = -6
    else:
        raise ValueError('\n' + 'Must select from the following EBUS strings:'
                         + '\n' + 'CalCS' + '\n' + 'CanCS' + '\n' + 'BenCS' +
                         '\n' + 'HumCS')
    return lat1, lat2

def drop_ensemble_dim(ds, x):
    """
    Since we load in the full ensemble of separate netCDF files, xArray
    automatically pops an 'ensemble' dimension onto the coordinate variables,
    which makes for frustrating indexing. This simply strips those away. HumCS
    is clarified here, because for some reason, TLONG doesn't have those
    dimensions. Who knows.
    """
    ds[x] = (('nlat','nlon'), ds[x][0])
    return ds

def main():
    EBU = sys.argv[1]
    VAR = sys.argv[2]
    print("Creating residuals for {} in the {}".format(VAR, EBU))
    OFFSHORE = 800 # distance to filter offshore EBUS bounds to.
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + '/' + EBU \
            + '/'
    ds = xr.open_mfdataset(fileDir + '*.nc', concat_dim='ensemble', 
                           chunks={'time': 10}, engine='netcdf4')
    # Reduce pesky coordinate ensemble dimension.
    ds = drop_ensemble_dim(ds, 'DXT')
    ds = drop_ensemble_dim(ds, 'TAREA')
    ds = drop_ensemble_dim(ds, 'REGION_MASK')
    ds = drop_ensemble_dim(ds, 'TLAT')
    ds = drop_ensemble_dim(ds, 'UAREA')
    if EBU != "HumCS":
        ds = drop_ensemble_dim(ds, 'TLONG')
    del ds['DYT']
    del ds['ANGLET']
    # Convert DXT to kilometers for easy filtering.
    ds['DXT'] = ds['DXT'] / 100 / 1000
    # Select latitudnal bounds
    lat1, lat2 = chavez_bounds(EBU)
    ds = ds.where(ds['TLAT'] >= lat1).where(ds['TLAT'] <= lat2)
    # Create a masked array for DXT since it doesn't follow the same NaN
    # structure.
    data = ds[VAR].isel(ensemble=0, time=0)
    data = np.ma.array(data, mask=np.isnan(data))
    dxt_dat = ds['DXT']
    dxt_dat = np.ma.array(dxt_dat, mask=np.isnan(data))
    ds['DXT'] = (('nlat','nlon'), dxt_dat)
    # Filter out rows without a coastline to reference (for distance to
    # coastline)
    regmask = ds['REGION_MASK']
    counter = 0
    for row in regmask:
        conditional = 0 in row.values
        if conditional == False:
            ds['DXT'][counter, :] = np.nan
        counter += 1
    # Now create a new variable for distance to coastl.
    x = ds['DXT'].values
    x = np.ma.array(x, mask=np.isnan(x))
    dxt_cum = np.cumsum(x[:, ::-1], axis=1)[:, ::-1]
    ds['DXT_Cum'] = (('nlat', 'nlon'), dxt_cum)
    # Filter out to within certain distance of coastline
    ds = ds.where(ds['DXT_Cum'] <= OFFSHORE)
    # GENERATE AND SAVE VARIANTS : FORCED/RESIDUALS +
    # AREA-WEIGHTED/NON-AREA-WEIGHTED
    ds_forced = ds[VAR].mean(dim='ensemble')
    ds_residuals = ds[VAR] - ds_forced
    ds_forced['UAREA'] = ds['UAREA']
    ds_residuals['UAREA'] = ds['UAREA']
    # AREA WEIGHTING
    ds_forced_AW = ((ds_forced * ds['UAREA']).sum(dim='nlat')
                       .sum(dim='nlon'))/ds['UAREA'].sum()
    ds_forced_AW.name = VAR + '_AW'
    ds_forced_AW = ds_forced_AW.to_dataset()
    ds_residuals_AW = ((ds_residuals * ds['UAREA']).sum(dim='nlat')
                       .sum(dim='nlon'))/ds['UAREA'].sum()
    ds_residuals_AW.name = VAR + '_AW'
    ds_residuals_AW = ds_residuals_AW.to_dataset()
    ds_forced = ds_forced.to_dataset()
    ds_residuals = ds_residuals.to_dataset()
    # Save as NetCDF.
    directory = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + '/' + \
                EBU + '/filtered_output/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    print("Saving forced signal to NetCDF...")
    ds_forced.to_netcdf(directory + EBU.lower() + '-' + VAR +
                        '-forced-signal-chavez-' + str(OFFSHORE) + 'km.nc')
    ds_forced_AW.to_netcdf(directory + EBU.lower() + '-' + VAR +
                        '-forced-signal-AW-chavez-' + str(OFFSHORE) + 'km.nc')
    print("Saving residuals to NetCDF...")
    ds_residuals.to_netcdf(directory + EBU.lower() + '-' + VAR +
                        '-residuals-chavez-' + str(OFFSHORE) + 'km.nc')
    ds_residuals_AW.to_netcdf(directory + EBU.lower() + '-' + VAR +
                        '-residuals-AW-chavez-' + str(OFFSHORE) + 'km.nc')

if __name__ == '__main__':
    main()
