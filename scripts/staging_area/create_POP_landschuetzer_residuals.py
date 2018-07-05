"""
Compute Landschuetzer POP Residuals

Takes in the Landschuetzer POP-remapped v2016 product and computes residuals
by detrending (4th order polynomial) and removing monthly climatology.
"""
import numpy as np
import pandas as pd
import xarray as xr
import esmtools as et
import sys


def remove_seasonal_cycle(x):
    """
    Remove the monthly climatology for a given grid cell.
    """
    if x.min().isnull():
        return xr.DataArray(np.nan)
    else:
        clim = x.groupby('time.month').mean('time')
        anom = x.groupby('time.month') - clim
        return anom

def main():
    filepath = '/glade/p/work/rbrady/Landschuetzer_pCO2/'
    filename = 'spco2_1982-2015_MPI_SOM-FFN_v2016_on_POP_gx1v6.conserve.nc'
    print("Loading dataset...")
    ds = xr.open_dataset(filepath + filename)
    ds = ds['fgco2_raw'].to_dataset()
    ds['time'] = pd.date_range('1982-01', '2016-01', freq='M')
    # Detrend via 4th-order polynomial
    print("Detrending...")
    ds = ds.stack(points=['nlat', 'nlon']).groupby('points') \
        .apply(et.ufunc.remove_polynomial_fit).unstack('points') 
    # Remove monthly climatology
    print("Removing monthly climatology...")
    ds = ds.stack(points=['nlat', 'nlon']).groupby('points') \
        .apply(remove_seasonal_cycle).unstack('points')
    # Save out file
    print("Saving to netCDF...")
    outDir = sys.argv[1]
    outFile = 'SOM-FFN.v2016.1982-2015.POP.residuals.nc'
    ds.to_netcdf(outDir + '/' + outFile)


if __name__ == '__main__':
    main()
