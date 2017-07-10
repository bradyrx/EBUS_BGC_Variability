# Author  : Riley X. Brady
# Date    : 06/06/2017, updated 07/07/2017
"""
Desc: This script will correlate any processed variable (i.e. it has gone
through the Extract_EBUS and generate_residuals scripts) and correlate/regress
it against ENSO, PDO, AMO, and SAM from the CVDP dataset that Adam Phillips
developed. As an end result, it will save the analysis information away as a
csv in the data/processed/EBU folder. These can be opened in a notebook for
analysis/plotting.
"""
# INPUT 1 : EBU
# INPUT 2 : Variable for correlating to climate indices.
# INPUT 3 : Boolean for smoothing (True == 12 month smoothing)
import glob
import sys
# Numerics
import numpy as np
import pandas as pd
import xarray as xr
from scipy import signal
from scipy import stats

def detrend_climate(x):
    return signal.detrend(x)

def smooth_series(x, length=12):
    series = pd.rolling_mean(x, length, center=False)
    series = series[(length-1)::]
    return series

def linear_regression(df, idx, x, y):
    # df is where you will store the output.
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    df['Slope'][idx] = slope
    df['R Value'][idx] = r_value
    df['R Squared'][idx] = r_value**2
    df['P-Value'][idx] = p_value
    return df

def main():
    EBU = sys.argv[1]
    VAR = sys.argv[2]
    SMOOTH = sys.argv[3]
    print("Operating on : {}".format(EBU))
    print("Correlating climate indices with {}...".format(VAR))
    if SMOOTH == "True":
        print "Data will be correlated after smoothing with a " + \
                "12-month rolling average."
    else:
        print "Data will NOT be smoothed."
    # Load in non-climate variable.
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + '/' + \
              EBU + '/filtered_output/'
    ds_var = xr.open_dataset(fileDir + EBU.lower() + '-' + VAR + \
                             '-residuals-AW-chavez-800km.nc')

    # Load in CVDP data.
    fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/extracted_vars/'
    ds_cvdp = xr.open_mfdataset(fileDir + '*.nc', decode_times=False,
                                concat_dim='ensemble')
    ds_cvdp = ds_cvdp.rename({'npo_pc_mon': 'npo',
                              'pdo_timeseries_mon': 'pdo',
                              'amo_timeseries_mon': 'amo',
                              'ipo_timeseries_mon': 'ipo',
                              'nao_pc_mon': 'nao',
                              'sam_pc_mon': 'sam'})
    times = pd.date_range('1920-01', '2016-01', freq='M')
    ds_cvdp['time'] = times

    # Detrend all of the climate indices
    ds_cvdp = ds_cvdp.apply(detrend_climate)

    # + - + - + - STATISTICAL ANALYSIS + - + - + -
    # Create a DataFrame to store correlation analysis on different climate
    # indices.
    index = np.arange(0, 34, 1)
    columns = ['Slope', 'R Value', 'R Squared', 'P-Value']
    df_enso = pd.DataFrame(index=index, columns=columns)
    df_pdo = pd.DataFrame(index=index, columns=columns)
    df_amo = pd.DataFrame(index=index, columns=columns)
    df_sam = pd.DataFrame(index=index, columns=columns)
    for idx in np.arange(0, 34, 1):
        ts1 = ds_var[VAR + '_AW'][idx].values
        ts2 = ds_cvdp['nino34'][idx].values
        ts3 = ds_cvdp['pdo'][idx].values
        ts4 = ds_cvdp['amo'][idx].values
        ts5 = ds_cvdp['sam'][idx].values
        if SMOOTH == "True":
            ts1 = smooth_series(ts1)
            ts2 = smooth_series(ts2)
            ts3 = smooth_series(ts3)
            ts4 = smooth_series(ts4)
            ts5 = smooth_series(ts5)
        print "Working on simulation " + str(idx+1) + " of 34..."
        # Run linear regressions
        df_enso = linear_regression(df_enso, idx, ts2, ts1)
        df_pdo = linear_regression(df_pdo, idx, ts3, ts1)
        df_amo = linear_regression(df_amo, idx, ts4, ts1)
        df_sam = linear_regression(df_sam, idx, ts5, ts1)
    directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
            'data/processed/' + EBU.lower() + '/region_correlations/'
    if SMOOTH == "True":
        df_enso.to_csv(directory + 'smoothed_' + VAR + '_vs_smoothed_enso_' + EBU)
        df_pdo.to_csv(directory + 'smoothed_' + VAR + '_vs_smoothed_pdo_' + EBU)
        df_amo.to_csv(directory + 'smoothed_' + VAR + '_vs_smoothed_amo_' + EBU)
        df_sam.to_csv(directory + 'smoothed_' + VAR + '_vs_smoothed_sam_' + EBU)
    else:
        df_enso.to_csv(directory + 'unsmoothed_' + VAR + '_vs_enso_' + EBU)
        df_pdo.to_csv(directory + 'unsmoothed_' + VAR + '_vs_pdo_' + EBU)
        df_amo.to_csv(directory + 'unsmoothed_' + VAR + '_vs_amo_' + EBU)
        df_sam.to_csv(directory + 'unsmoothed_' + VAR + '_vs_sam_' + EBU)

if __name__ == '__main__':
    main()
