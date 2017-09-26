"""
Global regression map
---------------------
Author: Riley X. Brady
Date: Sep 22, 2017

This script will regress/correlate CO2 flux anomalies from a given EBU onto a
global field of some other anomalies. The output is a netCDF for the given 
ensemble member that includes the regression coefficient, correlation
coefficient, and p-value. It's best to use a shell script to loop through
the ensemble members in parallel and pass them off to this script.

NOTE: Before running this script, you should run the generate_global_residuals
script to create individual global residual .nc files for each ensemble member.
This script needs to be pointed to that directory to function.

NOTE: Currently, this script compares to area-weighted residuals of
natural CO2 flux for the given EBU. This can be changed inline, or in the
future, an option to declare the EBU variable can be set. This script
also automatically smooths the global and EBU fields with a 12-month
moving average, since CO2 flux is so noisy.

INPUT 1: EBU indicator ("CalCS", "HumCS", "CanCS", "BenCS")
INPUT 2: Global variable to act as predictor for EBU gas flux.
INPUT 3: Months of lag time (global variable leads CO2 flux by this many months)
INPUT 4: Ensemble number (int between 0 and 33 inclusive)
INPUT 5: Directory pointing to the location of global residuals.
INPUT 6: Output directory for each simulations correlation grid.
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

def gridcell_correlations(x, y, lag):
    """
    This is the main analysis part of the script. Use this on an xarray 
    apply function to correlate the current gridcell residuals with
    the regional area-weighted time series. This definition uses the 
    global gridcell as the predictor, and smooths with a 12 month running
    mean to deal with the noisiness of CO2 flux residuals.

    The user needs to define the lag keyword which will automatically have
    the predictor variable lead the gas flux anomalies.

    It returns a Dataset with the slope, r-value, and p-value.
    """
    # Check for NaNs.
    if x.min().isnull():
        return xr.Dataset({'m': np.nan, 'r': np.nan, 'p': np.nan})
    else:
        # Smooth for 12 months by default.
        x = x.rolling(time=12).mean().dropna('time')
        y = y.rolling(time=12).mean().dropna('time')
        if lag == 0:
            m, _, r, p, _ = et.stats.linear_regression(x, y)
        else:
            m, _, r, p, _ = et.stats.linear_regression(x[:-lag], y[lag:])
        return xr.Dataset({'m': m, 'r': r, 'p': p})

def main():
    EBU = sys.argv[1]
    GLOBAL_VAR = sys.argv[2]
    LAG = int(sys.argv[3])
    ENS = int(sys.argv[4])
    GLOBAL_DIR = sys.argv[5]
    OUT_DIR = sys.argv[6]
    print("Working on " + GLOBAL_VAR + " regressions for simulation " +
          ens_str[ENS] + "...")
    # Load in area-weighted residuals for natural CO2 flux for the region.
    filedir = ('/glade/p/work/rbrady/EBUS_BGC_Variability/FG_ALT_CO2/' +
               EBU + '/filtered_output/' + EBU.lower() +
               '-FG_ALT_CO2-residuals-AW-chavez-800km.nc')
    # This is our 1152x1 regional time series for the given simulation.
    ds_regional = xr.open_dataset(filedir)
    ds_regional = ds_regional['FG_ALT_CO2_AW'][ENS]
    # Load in global residuals for this simulation.
    filedir = (GLOBAL_DIR + GLOBAL_VAR + '.' + ens_str[ENS] +
               '.global_residuals.nc')
    # This is our 1152x384x320 da of global residuals.
    ds_global = xr.open_dataset(filedir)
    # Perform computation!
    print("Beginning global correlations for #" + ens_str[ENS])
    correlation = ds_global[GLOBAL_VAR].stack(gridpoints=['nlat','nlon']) \
                                       .groupby('gridpoints') \
                                       .apply(gridcell_correlations, 
                                              y=ds_regional,
                                              lag=LAG) \
                                       .unstack('gridpoints')
    print("Finished global correlations for #" + ens_str[ENS])
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    out_file = (OUT_DIR + GLOBAL_VAR + '.FG_ALT_CO2.' + EBU + '.' +
                ens_str[ENS] + '.smoothed_global_regression.lag' +
                str(LAG) + '.nc')
    print("Saving #" + ens_str[ENS] + " to netCDF...")
    correlation.to_netcdf(out_file)

if __name__ == '__main__':
    main()        
                
