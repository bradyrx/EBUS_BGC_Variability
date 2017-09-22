# Author: Riley X. Brady
# Date: 07/12/2017
"""
Desc: This script performs all necessary regressions and sensitivity
calculations for a linear Taylor expansion of pCO2 on a gridcell-by-gridcell
basis. Currently, it applies an annual smoothing filter to both the climate
index and pCO2 terms. It stores the final product away as a netCDF file.
"""
# INPUT 1 : EBUS Name
# INPUT 2 : Climate Index
import sys
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

def smooth_series(x, length=12):
    series = pd.rolling_mean(x, length, center=False)
    series = series[(length-1)::]
    return series

def forced_mean(EBU, VAR):
    """
    Given an EBU and variable, this function loads in the forced signal of the
    full grid (not area-weighted) and computes the time-averaged mean over the
    historical period. It then returns a dataArray of that mean. It also
    gives the option to return the original dataset.
    """
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + \
            '/' + EBU + '/filtered_output/'
    fileName = EBU.lower() + '-' + VAR + '-forced-signal-chavez-800km.nc'
    ds = xr.open_dataset(fileDir + fileName)
    da_mean = ds[VAR].mean(dim='time')
    return da_mean

def main():
    EBU = sys.argv[1]
    CLIMVAR = sys.argv[2]
    print """
    Performing spatial regressions and computing sensitivity terms for a linear
    Taylor expansion of pCO2 in the {}. BOTH TIME SERIES ARE SMOOTHED WITH A 12
    MONTH ROLLING AVERAGE.
    """.format(EBU)
    # Compute sensitivities for the forced signal to use in the expansion
    # computations.
    print "Computing sensitivities across the grid for the ensemble mean."
    # generate ensemble means for each variable for sensitivity/buffer
    # calculations.
    DIC = forced_mean(EBU, 'DIC')
    ALK = forced_mean(EBU, 'ALK')
    pCO2 = forced_mean(EBU, 'pCO2SURF')
    SST = forced_mean(EBU, 'SST')
    SALT = forced_mean(EBU, 'SALT')
    # Compute buffers [naming is for merging into dataset later]
    gamma_DIC = (3*ALK*DIC - 2*DIC**2) / ((2*DIC - ALK) * (ALK-DIC))
    gamma_DIC.name = 'gamma_DIC'
    gamma_ALK = (-ALK**2) / ((2*DIC-ALK)*(ALK-DIC))
    gamma_ALK.name = 'gamma_ALK'
    # Compute sensitivities
    sens_SST = 0.0423 * pCO2
    sens_SST.name = 'sens_SST'
    sens_SALT = pCO2/SALT
    sens_SALT.name = 'sens_SALT'
    sens_DIC = (pCO2/DIC)*gamma_DIC
    sens_DIC.name = 'sens_DIC'
    sens_ALK = (pCO2/ALK)*gamma_ALK
    sens_ALK.name = 'sens_ALK'
    # Merge into one dataset for reference.
    sensitivities = xr.merge([gamma_DIC, gamma_ALK, sens_SST, sens_SALT,
                              sens_DIC, sens_ALK])
    # + + + LINEAR REGRESSION + + +
    print "Performing linear regressions."
    # Load in climate index.
    fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/processed/'
    ds_x = xr.open_dataset(fileDir + 'cvdp_detrended_BGC.nc')
    da_x = ds_x[CLIMVAR]
    # Perform analysis on each variable.
    regVars = ['pCO2SURF', 'DIC', 'ALK', 'SST', 'SALT']
    for var in regVars:
        fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + var + \
                '/' + EBU + '/filtered_output/'
        ds_y = xr.open_dataset(fileDir + EBU.lower() + '-' + var + \
                               '-residuals-chavez-800km.nc')
        da_y = ds_y[var]
        dims = da_y.shape
        results = np.empty([dims[0], dims[2], dims[3]])
        results[:] = np.nan
        print "Performing regressions with {}.".format(var)
        for e in np.arange(0, dims[0], 1):
            print "Simulation " + str(e+1) + " of 34..."
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
        sensitivities[var + '_slopes'] = (('ensemble', 'nlat', 'nlon'), \
                                          results)
    regression_results = sensitivities
    # Save final dataset with all of the slopes and sensitivities as a netCDF.
    directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
            'data/processed/' + EBU.lower() + '/pco2_taylor_spatial/'
    fileName = EBU.lower() + '-pco2-taylor-spatial-vs-' + CLIMVAR + \
            '-smoothed-pRemoved.nc'
    regression_results.to_netcdf(directory + fileName)

if __name__ == '__main__':
    main()
