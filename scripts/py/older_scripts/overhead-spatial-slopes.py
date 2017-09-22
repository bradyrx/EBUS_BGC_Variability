# Author: Riley X. Brady
# Date: 07/12/2017
"""
Desc: This script performs all the necessary regressions for a taylor series
expansion of pCO2 on a gridcell-by-gridcell basis. Currently, it applies an
annual smoothing filter to both the climate index and the pCO2 terms. It stores
the final product away as a netCDF file.
"""
# INPUT 1 : EBUS Name
# INPUT 2 : Predictor Variable
import sys
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

def smooth_series(x, length=12):
    series = pd.rolling_mean(x, length, center=False)
    series = series[(length-1)::]
    return series

def main():
    EBU = sys.argv[1]
    VARX = sys.argv[2]
    VARY = sys.argv[3]
    print """
    Running spatial regressions with {} as the predictor and {} as the
    dependent variable over the {}. BOTH TIME SERIES ARE SMOOTHED WITH A 12
    MONTH RUNNING MEAN.
    """.format(VARX, VARY, EBU)
    # Load in climate index of choosing.
    fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/processed/'
    ds_x = xr.open_dataset(fileDir + 'cvdp_detrended_BGC.nc')
    da_x = ds_x[VARX]
    # Load in criterion variable.
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VARY + '/' + \
        EBU + '/filtered_output/'
    ds_y = xr.open_dataset(fileDir + EBU.lower() + '-' + VARY + \
        '-residuals-chavez-800km.nc')
    da_y = ds_y[VARY]
    # Perform linear regression
    dims = da_y.shape
    results = np.empty([dims[0], dims[2], dims[3]])
    results[:] = np.nan
    for e in np.arange(0, dims[0], 1):
        print "Working on Ensemble " + str(e+1) + " of 34..."
        xdata = da_x[e].values
        xdata = smooth_series(xdata)
        ydata = da_y[e].values
        for a in np.arange(0, dims[2], 1):
            for b in np.arange(0, dims[3], 1):
                temp_y = ydata[:, a, b]
                temp_y = smooth_series(temp_y)
                m, _, _, p, _ = stats.linregress(xdata, temp_y)
                if p <= 0.05:
                    results[e, a, b] = m
    directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
            'data/processed/' + EBU.lower() + '/spatial_correlations/'
    fileName = EBU.lower() + '-smoothed-' + VARX + '-smoothed-' + \
            VARY + '-spatial-regressions-pRemoved'
    np.save(directory + fileName, results)

if __name__ == '__main__':
    main()
