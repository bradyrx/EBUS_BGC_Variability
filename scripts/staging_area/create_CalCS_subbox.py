"""
Create CalCS Subbox
-------------------
Author: Riley X. Brady
Date: 01/09/2018

This is a very specialized script. Given a variable for the California Current,
it will extract a specified box and area-weight it into its own separate time
series. It will not save out every individual ensemble member, but rather a
netCDF of the ensemble mean for the box and the ensemble residuals for that box.

This script depends on EBUS_Extraction.py already having been run on the given
variable for the California Current.

NOTE: Currently, this script is defaulted to taking either "onshore" or "offshore"
as the argument. These are the boxes that were created for the PDO/ENSO correlation
for the California Current. You can modify this script to accept any box dimensions.

ONSHORE:
nlon (18:20)
nlat (22:25)

OFFSHORE:
nlon (13:15)
nlat (27:30)

INPUT 1: Variable (str)
INPUT 2: "Onshore" or "Offshore"
"""
import sys
import os
import glob
import xarray as xr

def get_indices(str):
    """
    Given a string ("offshore" or "onshore"), returns the x0, x1, y0, and y1
    indices for slicing to the desired box.
    """
    if str.lower() == 'offshore':
        x0,x1,y0,y1 = [13,15,27,30]
    elif str.lower() == 'onshore':
        x0,x1,y0,y1 = [18,20,22,25]
    else:
        raise ValueError("Incorrect box declaration. Need to pass either" +
              "'offshore' or 'onshore'")
    return x0,x1,y0,y1

def drop_ensemble_dim(ds, x):
    """
    Since we load in the full ensemble of separate netCDF files, xArray
    automatically pops an 'ensemble' dimension onto the coordinate variables,
    which makes for frustrating indexing. This simply strips those away. HumCS
    is clarified here, because for some reason, TLONG doesn't have those
    dimensions. Who knows.
    """
    ds[x] = (('nlat', 'nlon'), ds[x][0])
    return ds

def main():
    VAR = sys.argv[1]
    REG = sys.argv[2]
    print("Creating " + REG.lower() + " time series for " + VAR + " in the CalCS...")
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + '/CalCS/')
    ds = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
    ds = drop_ensemble_dim(ds, 'TLAT')
    ds = drop_ensemble_dim(ds, 'TLONG')
    ds = drop_ensemble_dim(ds, 'TAREA')
    # Slice into designated box
    x0,x1,y0,y1 = get_indices(REG)
    ds = ds.isel(nlon=slice(x0,x1+1), nlat=slice(y0,y1+1))
    # Area-weight into one time series
    area = ds['TAREA']
    da = ds[VAR]
    da = ((da * area).sum('nlat').sum('nlon'))/area.sum()
    da.name = VAR
    ds = da.to_dataset()
    # Create ensemble mean and residuals.
    ds_forced = ds.mean('ensemble')
    ds_residuals = ds[VAR] - ds_forced
    # Save out.
    directory = ('/glade/p/work/rbrady/EBUS_BGC_Variability/CalCS_Boxes/' +
                 REG.lower() + '/' + VAR + '/')
    if not os.path.exists(directory):
        os.makedirs(directory)
    print("Saving forced signal to NetCDF...")
    ds_forced.to_netcdf(directory + 'CalCS.' + VAR + '.' + REG.lower() +
                        '.forced-signal.nc')
    print("Saving residuals to NetCDF...")
    ds_residuals.to_netcdf(directory + 'CalCS.' + VAR + '.' + REG.lower() +
                        '.residuals.nc')

if __name__ == '__main__':
    main()
