# EBUS Site Extraction
# Author: Riley X. Brady
# Date: 05/31/2017
# Purpose: Take in a global netCDF, extract an upwelling system, save as a netCDF all cleaned up with datetime
# axis and so on. Meant to be used with HTC (e.g. with GNU Parallel).

# NOTE : For now, this script is coded for the CCS and for FG_CO2 (as it contains the conversion in it). It can be modified in the future to be more robust.

# INPUT 1 : NetCDF of ensemble member to be worked on. (Ideally global; should be full path name, e.g. /glade/scratch/.../001.nc)
# INPUT 2 : Variable name (shell string).
# INPUT 3 : Output directory, where processed .nc files will land. The directory should end in a backslash.

# Allow a file input to be referenced.
import sys

# Matrix Analysis
import numpy as np
import pandas as pd
import xarray as xr

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

    # Convert to sea-air flux in mol/m2/yr
    dataVar = sys.argv[2] # Input on command line; usually a shell variable.
    ds[dataVar] = ds[dataVar] * ((-1 * 3600 * 24 * 365.25) / (1000 * 100))
    
    # Convert area to m2
    ds['TAREA'] = ds['TAREA'] / (100 * 100)

    # Drop unnecessary bits
    del ds['time_bound']
    del ds['d2']

    # Add in some metadata
    ds.attrs['carbon flux units'] = "mol/m2/yr"
    ds.attrs['area units'] = "m2"

    # California (for now; extensive offshore region)
    a, c = find_indices(ds['TLAT'].values, ds['TLONG'].values, 25, 215)
    b, d = find_indices(ds['TLAT'].values, ds['TLONG'].values, 46, 260)

    # Slice out CCS, cover 1920 to 2015 per Adam Phillip's climate indices.
    ds = ds.sel(nlat=slice(a, b), nlon=slice(c, d), time=slice('1920-01', '2015-12'))

    # File output as netCDF
    ens = fileName[-20:-17] # This works if you maintain the standard naming convention of VAR.ENS.192001-210012.nc
    newFile = dataVar + '.' + ens + '.CCS.192001-201512.nc'
    outDir = sys.argv[3]
    ds.to_netcdf(outDir + newFile)

if  __name__ == '__main__':
    main()


