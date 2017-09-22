# Author: Riley X. Brady
# Date: 07/10/2017
"""
Desc: This script will perform a gridcell-by-gridcell correlation between two
different variables of a given EBUS. This differs from the other correlation
scripts which compute a correlation between area-weighted averages over the
full region. The product of this script is to save a numpy matrix of
correlation r-values which can be used in a notebook to visualize the spatial
relationships in correlations.
"""
# INPUT 1 : EBUS Name
# INPUT 2 : Predictor Variable
# INPUT 3 : Dependent Variable
import sys
import glob
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from scipy import signal
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cmocean
from constants import *

def detrend_series(x):
    return signal.detrend(x)

def smooth_series(x, length=12):
    series = pd.rolling_mean(x, length, center=False)
    series = series[(length-1)::]
    return series

def main():
    EBU = sys.argv[1]
    VARX = sys.argv[2]
    VARY = sys.argv[3]
    # x variable might be a climate index which has a different directory.
    if VARX not in ('nino34', 'pdo', 'amo', 'sam'):
        fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VARX + '/' + \
            EBU + '/filtered_output/'
        ds_x = xr.open_dataset(fileDir + EBU.lower() + '-' + VARX + \
            '-residuals-chavez-800km.nc')
        CLIM=False
    else:
        fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/processed/'
        ds_x = xr.open_dataset(fileDir + 'cvdp_detrended_BGC.nc')
        CLIM=True
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VARY + '/' + \
        EBU + '/filtered_output/'
    ds_y = xr.open_dataset(fileDir + EBU.lower() + '-' + VARY + \
        '-residuals-chavez-800km.nc')
    # Perform linear regression
    dims = ds_y[VARY].shape
    results = np.empty([dims[0], dims[2], dims[3]])
    results[:] = np.nan
    # Climate indices don't have multiple dimensions so just doing this
    # analysis totally separate to keep the code readable.  
    if CLIM:
        for e in np.arange(0, dims[0], 1):
            print "Working on Ensemble " + str(e+1) + " of 34..."
            xdata = ds_x[VARX][e].values
            xdata = smooth_series(xdata)
            ydata = ds_y[VARY][e]
            for a in np.arange(0, dims[2], 1):
                for b in np.arange(0, dims[3], 1):
                    tempy = ydata[:, a, b].values
                    tempy = smooth_series(tempy)
                    if ~np.isnan(tempy[0]):
                        _, _, r, p, _ = stats.linregress(xdata, tempy)
                        if p <= 0.05:
                            results[e, a, b] = r
                        else:
                            results[e, a, b] = -999
    directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
        'data/processed/' + EBU.lower() + '/spatial_correlations/'
    np.save(directory + EBU.lower() + '-smoothed-' + VARY + '-smoothed-' + \
        VARX + '-spatial-correlations', results)

if __name__ == '__main__':
    main()
