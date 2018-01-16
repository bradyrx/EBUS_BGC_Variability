"""
Overhead Spatial Correlation
----------------------------
Author: Riley X. Brady
Date: Oct 10, 2017

This script will do a gridcell correlation over an EBUS with some other 
time series. This differs from the scripts that will just correlate with 
the area-weighted EBUS, thus offering a more finer spatial assessment.

E.g. you can correlate California Current FG_CO2 gridcell residuals with
the NPGO or PDO or ENSO.

NOTE: This script is currently set up to correlate with FG_CO2 residuals.
You can make this an input option later if you'd like.

NOTE: This script is also written to handle PDO, ENSO, AMO, etc. from the
climate diagnostics package as well as NPGO. You will have to add functionality
for other single time series in the future. 

INPUT 1: Str for EBUS ('CalCS', 'CanCS', 'HumCS', 'BenCS')
INPUT 2: Predictor climate variable for the residuals 
    ('NPGO', 'PDO', 'ENSO', 'AMO', etc.)
INPUT 3: Int for ensemble member number (0..34)
INPUT 4: Int for number of months to lag (0 is no lag).
INPUT 5: Int for how many months to smooth by (0 is no smoothing). 
"""
import sys
import os
import numpy as np
import xarray as xr
import esmtools as et

ens_str = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
           '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
           '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
           '102', '103', '104', '105']

def gridcell_correlations(y, x, lag, smooth):
    """
    This is the main analysis part of the script. use this on an xarray apply
    function to correlate the current gridcell residuals with the climate
    time series. This definition uses the climate time series as the predictor
    and the EBU time series as the predicted.

    You can set a lag of N months.

    Smooth is a boolean of whether or not to smooth. (In the future, you can
    make this an int on how many months to smooth, with 0 being no smoothing)

    It returns a dataset with the slope, r-value, and p-value.
    """
    # Check for NaNs (coastlines).
    if y.min().isnull():
        return xr.Dataset({'m': np.nan, 'r': np.nan, 'p': np.nan})
    else:
        if smooth != 0:
            x = x.rolling(time=smooth).mean().dropna('time')
            y = y.rolling(time=smooth).mean().dropna('time')
        if lag == 0:
            m, _, r, p, _ = et.stats.linear_regression(x, y)
        else:
            m, _, r, p, _ = et.stats.linear_regression(x[:-lag], y[lag:])
        return xr.Dataset({'m': m, 'r': r, 'p': p})

def main():
    EBU = sys.argv[1]
    VARX = sys.argv[2]
    ENS = int(sys.argv[3])
    LAG = int(sys.argv[4])
    SMOOTH = int(sys.argv[5])
    print("Working on " + VARX + " regressions for simulation " + 
          ens_str[ENS] + " over the " + EBU + "...")
    if VARX == 'NPGO':
        """
        This was a custom EOF procedure, so the NC files are very different 
        from the way Adam Phillips set his up.
        """
        filepath = '/glade/p/work/rbrady/EBUS_BGC_Variability/NPGO/'
        filename = 'NPGO.' + ens_str[ENS] + '.1920-2015.nc'
        ds_x = xr.open_dataset(filepath + filename)
        # Pull out a DA of the principal component time series.
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
        ds_x = ds_x[VARX.lower()][ENS]
    # Load in the co2 flux anomalies.
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/FG_CO2/' +
                EBU + '/filtered_output/')
    filename = EBU.lower() + '-FG_CO2-residuals-chavez-800km.nc'
    ds_y = xr.open_dataset(filepath + filename)
    ds_y = ds_y['FG_CO2'][ENS]
    # Run the correlation.
    correlation = ds_y.stack(gridpoints=['nlat','nlon']) \
                      .groupby('gridpoints') \
                      .apply(gridcell_correlations,
                             x=ds_x,
                             lag=LAG,
                             smooth=SMOOTH) \
                      .unstack('gridpoints')
    print("Finished regional correlations for #" + ens_str[ENS])
    OUT_DIR = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' +
               'regional_regressions/' + EBU + '/' + VARX + '/' +
               'lag' + str(LAG) + '/')
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    if SMOOTH != 0: # Save with smoothing in file name.
        out_file = (OUT_DIR + VARX + '.FG_CO2.' + EBU + '.' +
                    ens_str[ENS] + '.smoothed' + str(SMOOTH) + 
                    '_regional_regression.lag' + str(LAG) + '.nc')
    else:
        out_file = (OUT_DIR + VARX + '.FG_CO2.' + EBU + '.' +
                    ens_str[ENS] + '.unsmoothed_regional_regression.lag' +
                    str(LAG) + '.nc')
    print("Saving #" + ens_str[ENS] + " to netCDF...")
    correlation.to_netcdf(out_file)

if __name__ == '__main__':
    main()
