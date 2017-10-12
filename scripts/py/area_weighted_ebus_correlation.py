"""
Area Weighted EBUS Correlation
----------------------------
Author: Riley X. Brady
Date: Oct 11, 2017

This script will correlate the area-weighted residuals time series for a given
EBUS with a climate index time series (from its corresponding ensemble member).
This is an updated script from the old version that used to use numpy arrays.
This will use xarray to its fully capacity and output an entire ensemble of 
correlations as a single netCDF file.

E.g. you can correlate the entire California Current FG_ALT_CO2 residuals with
the NPGO index. You can also specify whatever lag and smoothing necessary.

NOTE: There is probably a way to do this with "apply" but I can't figure out
how. It isn't as simple as doing .groupby('ensemble') and then calling
ds.x and ds.y in the apply function.

NOTE: This script is currently set up to correlate with FG_ALT_CO2 residuals.
You can make this an input option later if you'd like.

NOTE: This script is also written to handle PDO, ENSO, AMO, etc. from the
climate diagnostics package as well as NPGO. You will have to add functionality
for other single time series in the future. 

INPUT 1: Str for EBUS ('CalCS', 'CanCS', 'HumCS', 'BenCS')
INPUT 2: Predictor climate variable for the residuals 
    ('NPGO', 'PDO', 'ENSO', 'AMO', etc.)
INPUT 3: Dependent variable in the EBU
    (FG_ALT_CO2, FG_CO2, ...)
INPUT 4: Int for number of months to lag (0 is no lag).
INPUT 5: Int for how many months to smooth by (0 is no smoothing). 
"""
import glob
import sys
import os
import numpy as np
import xarray as xr
import esmtools as et

def main():
    EBU = sys.argv[1]
    VARX = sys.argv[2]
    VARY = sys.argv[3]
    LAG = int(sys.argv[4])
    SMOOTH = int(sys.argv[5])
    print("Working on " + VARX + " regressions over the " + EBU + 
          " with " + str(LAG) + "mo. lag and " + str(SMOOTH) +
          " mo. smoothing...")
    if VARX == 'NPGO':
        """
        This was a custom EOF procedure, so the NC files are very different 
        from the way Adam Phillips set his up.
        """
        filepath = '/glade/p/work/rbrady/NPGO/'
        ds_x = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
        ds_x = ds_x['pc']
    else:
        """
        This assumes the variable can be found in Adam Phillip's climate
        diagnostics output. Need to edit this loading if that's not the
        case.
        """
        filepath = '/glade/p/work/rbrady/cesmLE_CVDP/processed/'
        filename = 'cvdp_detrended_BGC.nc'
        ds_x = xr.open_dataset(filepath + filename)
        ds_x = ds_x[VARX.lower()]
    # Load in the co2 flux anomalies.
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + VARY + '/' + 
                EBU + '/filtered_output/')
    filename = EBU.lower() + '-' + VARY + '-residuals-AW-chavez-800km.nc'
    ds_y = xr.open_dataset(filepath + filename)
    ds_y = ds_y[VARY + '_AW']
    # Smooth if necessary.
    if SMOOTH != 0:
            ds_x = ds_x.rolling(time=SMOOTH).mean().dropna('time')
            ds_y = ds_y.rolling(time=SMOOTH).mean().dropna('time')
    # Combine into one dataset.
    ds_x.name = 'x'
    ds_y.name = 'y'
    ds = ds_x.to_dataset()
    ds['y'] = ds_y
    # Run the correlation (Here can definitely be improved..)
    m, r, p = ([] for i in range(3))
    for label, group in ds.groupby('ensemble'):
        """
        Run a simple correlation/regression, but need to check for all of the
        optional lag and smoothing settings.
        """
        if LAG == 0:
            M, _, R, P, _ = et.stats.linear_regression(group.x, group.y)
            m.append(M)
            r.append(R)
            p.append(P)
        else:
            M, _, R, P, _ = et.stats.linear_regression(group.x[:-LAG],
                                                       group.y[LAG:])
            m.append(M)
            r.append(R)
            p.append(P)
    # Set up in dataset.
    ds = xr.Dataset({'m': ('ensemble', m),
                     'r': ('ensemble', r),
                     'p': ('ensemble', p)})
    print("Finished regional correlations.")
    OUT_DIR = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' +
               'area_weighted_regional_regressions/' + EBU + '/' + VARY + '/' + 
               VARX + '/') 
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    if SMOOTH != 0: # Save with smoothing in file name.
        out_file = (OUT_DIR + VARX + '.' + VARY + '.' + EBU + '.smoothed' +
                    str(SMOOTH) + '.area_weighted_regional_regression.lag' +
                    str(LAG) + '.nc')
    else:
        out_file = (OUT_DIR + VARX + '.' + VARY + '.' + EBU +
                    '.unsmoothed.area_weighted_regional_regression.lag' +
                    str(LAG) + '.nc')
    print("Saving to netCDF...")
    ds.to_netcdf(out_file)

if __name__ == '__main__':
    main()
