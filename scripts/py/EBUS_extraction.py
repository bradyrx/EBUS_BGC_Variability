# EBUS Site Extraction
# Author: Riley X. Brady
# Date: 05/31/2017
# Purpose: Take in a global netCDF, extract an upwelling system, save as a netCDF all cleaned up with datetime
# axis and so on. Meant to be used with HTC (e.g. with GNU Parallel).

# INPUT 1 : NetCDF of ensemble member to be worked on. (Ideally global; should be full path name, e.g. /glade/scratch/.../001.nc)
# INPUT 2 : Variable name (shell string).
# INPUT 3 : EBUS identifier : CalCS, BenCS, CanCS, HumCS
# INPUT 4 : Output directory, where processed .nc files will land. The directory should end in a backslash.

# Allow a file input to be referenced.
import sys

# Matrix Analysis
import numpy as np
import pandas as pd
import xarray as xr

def detect_EBUS(x):
    # Will return latitude and longitude boundings for the selected region.
    # x should be a string from the following:
        # CalCS : California Current
        # BenCS : Benguela Current
        # CanCS : Canary Current
        # HumCS : Humboldt Current
    if x == "CalCS":
        lat1 = 25
        lat2 = 46
        lon1 = 215
        lon2 = 260
    elif x == "BenCS":
        lat1 = -30
        lat2 = -16
        lon1 = 0
        lon2 = 20
    elif x == "CanCS":
        lat1 = 19 
        lat2 = 33 
        lon1 = 330
        lon2 = 359
    elif x == "HumCS":
        lat1 = -20
        lat2 = 0
        lon1 = 260
        lon2 = 290
    else:
        raise ValueError('\n' + 'Must select from the following EBUS strings:'
                         + '\n' + 'CalCS' + '\n' + 'CanCS' + '\n' + 'BenCS' +
                         '\n' + 'HumCS')
    return lat1, lat2, lon1, lon2

def find_indices(latGrid, lonGrid, latPoint, lonPoint):
    dx = lonGrid - lonPoint
    dy = latGrid - latPoint
    reducedGrid = abs(dx) + abs(dy)
    min_ix = np.nanargmin(reducedGrid)
    i, j = np.unravel_index(min_ix, reducedGrid.shape)
    return i, j

def main():
    fileName = sys.argv[1] # System input (filename placed after script name on command line)
    print("Operating on : {}".format(fileName))
    pandaTimes = pd.date_range('1920-01', '2101-01', freq='M')
    ds = xr.open_dataset(fileName, decode_times=False)
    ds.coords['time'] = pandaTimes
    ds.attrs = {} # Clear out the legacy attributes from CESM and NCO.
    ds = ds.squeeze() # Get rid of any 1D leftovers from a depth variable.
    # Convert to sea-air flux in mol/m2/yr
    dataVar = sys.argv[2] # Variable name (e.g. FG_CO2) 
    if (dataVar == "FG_CO2") or (dataVar == "FG_ALT_CO2"):
        ds[dataVar] = ds[dataVar] * ((-1 * 3600 * 24 * 365.25) / (1000 * 100))
        ds.attrs['carbon flux units'] = "mol/m2/yr"
    # Convert area to m2
    ds['TAREA'] = ds['TAREA'] / (100 * 100)
    ds['UAREA'] = ds['UAREA'] / (100 * 100)
    # Drop unnecessary bits
    del ds['time_bound']
    # Add in some metadata
    ds.attrs['area units'] = "m2"
    # Get region bounds for EBU. If Benguela, need to convert the longitude
    # grid to go over the equator.
    EBUS_NAME = sys.argv[3]
    if EBUS_NAME == "BenCS":
        lon = np.asarray(ds['TLONG'])
        mask = (lon > 180)
        lon[mask] = lon[mask] - 360
        ds['TLONG'] = (('nlat','nlon'), lon) # Now -180 to 180 range.
    lat1, lat2, lon1, lon2 = detect_EBUS(EBUS_NAME)
    a, c = find_indices(ds['TLAT'].values, ds['TLONG'].values, lat1, lon1)
    b, d = find_indices(ds['TLAT'].values, ds['TLONG'].values, lat2, lon2)
    # Slice out EBUS, cover 1920 to 2015 per Adam Phillip's climate indices.
    ds = ds.sel(nlat=slice(a, b), nlon=slice(c, d), time=slice('1920-01', '2015-12'))
    # File output as netCDF
    ens = fileName[-20:-17] # This works if you maintain the standard naming convention of VAR.ENS.192001-210012.nc
    newFile = dataVar + '.' + ens + '.' + EBUS_NAME + '.192001-201512.nc'
    outDir = sys.argv[4]
    ds.to_netcdf(outDir + newFile)

if  __name__ == '__main__':
    main()


