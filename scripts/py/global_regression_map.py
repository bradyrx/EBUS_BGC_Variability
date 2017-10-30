"""
Global regression map
---------------------
Author: Riley X. Brady
Date: Sep 22, 2017

This script will regress/correlate CO2 flux anomalies from a given EBU onto a
global field of some other anomalies. The output is a netCDF for the given 
ensemble member that includes the regression coefficient, correlation
coefficient, and p-value. It's best to use a shell script to loop through
the ensemble members and pass them off to this script.

NOTE: Before running this script, you should run the generate_global_residuals
script to create individual global residual .nc files for each ensemble member.
This script needs to be pointed to that directory to function.

NOTE: Currently, this script compares to area-weighted residuals of
natural CO2 flux for the given EBU. This can be changed inline, or in the
future, an option to declare the EBU variable can be set. Otherwise, you can
use this script to look at how a climate index maps globally with some 
anomaly field.

INPUT 1: Dependent variable  indicator ("CalCS", "HumCS", "CanCS", "BenCS")
         for FG_ALT_CO2, or climate index indicator ("NPGO", "PDO", etc.)
INPUT 2: Global variable to act as predictor for EBU gas flux.
INPUT 3: Months of lag time (global variable leads CO2 flux by this many months)
INPUT 4: Ensemble number (int between 0 and 33 inclusive)
INPUT 5: Boolean for smoothing (If True, smooths for 12 months)
"""
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr
import esmtools as et

ens_str = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
           '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
           '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
           '102', '103', '104', '105']

def gridcell_correlations(x, y, lag, smooth):
    """
    This is the main analysis part of the script. Use this on an xarray 
    apply function to correlate the current gridcell residuals with
    the regional area-weighted time series. This definition uses the 
    global gridcell as the predictor, and smooths with a 12 month running
    mean to deal with the noisiness of CO2 flux residuals.

    The user needs to define the lag keyword which will automatically have
    the predictor variable lead the gas flux anomalies.

    The user also needs to define the smooth keyword to either turn on
    12 month smoothing or to keep smoothing off.

    It returns a Dataset with the slope, r-value, and p-value.
    """
    # Check for NaNs.
    if x.min().isnull():
        return xr.Dataset({'m': np.nan, 'r': np.nan, 'p': np.nan})
    else:
        # Smooth by 12 months if indicated.
        if smooth:
            x = x.rolling(time=12).mean().dropna('time')
            y = y.rolling(time=12).mean().dropna('time')
        if lag == 0:
            m, _, r, p, _ = et.stats.linear_regression(x, y)
        else:
            m, _, r, p, _ = et.stats.linear_regression(x[:-lag], y[lag:])
        return xr.Dataset({'m': m, 'r': r, 'p': p})

def main():
    VARY = sys.argv[1]
    GLOBAL_VAR = sys.argv[2]
    LAG = int(sys.argv[3])
    ENS = int(sys.argv[4])
    SMOOTH = sys.argv[5]
    print("Working on " + GLOBAL_VAR + " regressions for simulation " +
          ens_str[ENS] + "...")
    # Load in area-weighted residuals for natural CO2 flux for the region
    # or a climate index indicator.
    if VARY in ['SAM', 'NINO34', 'PDO', 'AMO']:
        filepath = ('/glade/p/work/rbrady/cesmLE_CVDP/processed/')
        filename = 'cvdp_detrended_BGC.nc'
        ds_regional = xr.open_dataset(filepath + filename)
        ds_regional = ds_regional[VARY.lower()][ENS]
    elif VARY == 'NPGO':
        filepath = '/glade/p/work/rbrady/NPGO/'
        filename = 'NPGO.' + ens_str[ENS] + '.1920-2015.nc'
        ds_regional = xr.open_dataset(filepath + filename)
        ds_regional = ds_regional['pc']
    else:
        filedir = ('/glade/p/work/rbrady/EBUS_BGC_Variability/FG_ALT_CO2/' +
               VARY + '/filtered_output/' + VARY.lower() +
               '-FG_ALT_CO2-residuals-AW-chavez-800km.nc')
        # This is our 1152x1 regional time series for the given simulation.
        ds_regional = xr.open_dataset(filedir)
        ds_regional = ds_regional['FG_ALT_CO2_AW'][ENS]
    # Load in global residuals for this simulation.
    GLOBAL_DIR = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' + 
                  'global_residuals/' + GLOBAL_VAR + '/')
    filedir = (GLOBAL_DIR + 'residual.' + GLOBAL_VAR + '.' + ens_str[ENS] +
               '.192001-201512.nc')
    # This is our 1152x384x320 da of global residuals.
    ds_global = xr.open_dataset(filedir)
    # Determine if ocean or atmosphere output for stacking.
    if ds_global.dims.__contains__('nlon'):
        OCEAN=True
    else:
        OCEAN=False
    # Perform computation!
    print("Beginning global correlations for #" + ens_str[ENS])
    if OCEAN: # Ocean grid
        correlation = ds_global[GLOBAL_VAR].stack(gridpoints=['nlat','nlon']) \
                                           .groupby('gridpoints') \
                                           .apply(gridcell_correlations, 
                                                  y=ds_regional,
                                                  lag=LAG,
                                                  smooth=SMOOTH) \
                                           .unstack('gridpoints')
    else: # Atmospheric grid
        correlation = ds_global[GLOBAL_VAR].stack(gridpoints=['lat','lon']) \
                                           .groupby('gridpoints') \
                                           .apply(gridcell_correlations,
                                                  y=ds_regional,
                                                  lag=LAG,
                                                  smooth=SMOOTH) \
                                           .unstack('gridpoints')
    print("Finished global correlations for #" + ens_str[ENS])
    OUT_DIR = ('/glade/p/work/rbrady/EBUS_BGC_Variability/global_regressions/' +
               GLOBAL_VAR + '/' + VARY + '/lag' + str(LAG) + '/')
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    if SMOOTH == "True": # Save with smoothing in filename
        if VARY in ['CalCS', 'HumCS', 'CanCS', 'BenCS']:
            out_file = (OUT_DIR + GLOBAL_VAR + '.FG_ALT_CO2.' + VARY + '.' +
                        ens_str[ENS] + '.smoothed_global_regression.lag' +
                        str(LAG) + '.nc')
        else:
            out_file = (OUT_DIR + GLOBAL_VAR + '.' + VARY + '.' +
                        ens_str[ENS] + '.smoothed_global_regression.lag' +
                        str(LAG) + '.nc')
    else:
        if VARY in ['CalCS', 'HumCS', 'CanCS', 'BenCS']:
            out_file = (OUT_DIR + GLOBAL_VAR + '.FG_ALT_CO2.' + VARY + '.' + 
                        ens_str[ENS] + '.unsmoothed_global_regression.lag' +
                        str(LAG) + '.nc')
        else:
            out_file = (OUT_DIR + GLOBAL_VAR + '.' + VARY + '.' +
                        ens_str[ENS] + '.unsmoothed_global_regression.lag' +
                        str(LAG) + '.nc')
    print("Saving #" + ens_str[ENS] + " to netCDF...")
    correlation.to_netcdf(out_file)

if __name__ == '__main__':
    main()        
                
