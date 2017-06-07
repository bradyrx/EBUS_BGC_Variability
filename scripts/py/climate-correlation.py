# Author  : Riley X. Brady
# Date    : 06/06/2017
# Purpose : Take in data from an EBUS (for now optimized for FG_CO2) and
# correlate/regress it against a few climate indices from the CVDP dataset that
# Adam Phillips developed.

# UNIX-style globbing
import glob

# Numerics
import numpy as np
import pandas as pd
import xarray as xr
from scipy import signal
from scipy import stats
import statsmodels.api as sm

# Visualization
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import seaborn as sns
sns.set(color_codes=True)

def detrend_climate(x):
    return signal.detrend(x)

def smooth_series(x, len):
    return pd.rolling_mean(x, len)

def seaborn_jointplot(carbonData, climateData, ensNum):
    # Make sure these data are presented as pandas dataframes. You can do this
    # inline below by saying "ds[ens].to_pandas()"
    df = pd.DataFrame({'Nino3.4':climateData,
                       'FG_CO2':carbonData})
    fig = plt.figure(figsize=(6,6))
    with sns.axes_style("white"):
        sns.jointplot(x='Nino3.4', y='FG_CO2', data=df,
                      kind='reg', space=0, color='k')
        plt.savefig('figs/smoothed_jointplot_nino_' + ensNum + '.png', dpi=1000,
                    transparent=True)
        plt.close(fig)

def autocorr_plot(ts1, ts2, ts3, ts4, ensNum):
    fig = plt.figure(figsize=(12,12))
    ax1 = fig.add_subplot(411)
    ax1.set_ylabel("FG_CO2 Autocorrelation")
    sm.graphics.tsa.plot_acf(ts1, lags=40, ax=ax1)
    ax2 = fig.add_subplot(412)
    ax2.set_ylabel("Nino 3.4 Autocorrelation")
    sm.graphics.tsa.plot_acf(ts2, lags=40, ax=ax2)
    ax3 = fig.add_subplot(413)
    ax3.set_ylabel("PDO Autocorrelation")
    sm.graphics.tsa.plot_acf(ts3, lags=40, ax=ax3)
    ax4 = fig.add_subplot(414)
    ax4.set_ylabel("NPO Autocorrelation")
    sm.graphics.tsa.plot_acf(ts4, lags=40, ax=ax4)
    plt.savefig('figs/autocorrelation_' + ensNum + '.svg', dpi=1000,
                transparent=True)
    plt.close(fig)

def linear_regression(x, y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, r_value, r_value**2, p_value

def main():
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/FG_CO2/'
    ds_gas = xr.open_mfdataset(fileDir + '*.nc', concat_dim='ensemble')
    ens = ['001', '002', '009', '010', '011', '012', '013', '014', '015',
           '016', '017', '018', '019', '020', '021', '022', '023', '024',
           '025', '026', '027', '028', '029', '030', '031', '032', '033',
           '034', '035', '101', '102', '103', '104', '105']
    ds_gas['ensemble'] = ens

    # Subtract out the ensemble mean from all members (create residuals)
    ds_residuals = ds_gas['FG_CO2'] - ds_gas['FG_CO2'].mean(dim='ensemble')

    # Area-weighting. ds_residuals is now the area-weighted average time
    # series.
    ds_residuals = ((ds_residuals * ds_gas['TAREA'])
                    .sum(dim='nlat').sum(dim='nlon'))/ds_gas['TAREA'][0].sum()

    # Load in CVDP data.
    fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/extracted_vars/'
    ds_cvdp = xr.open_mfdataset(fileDir + '*.nc', decode_times=False,
                                concat_dim='ensemble')
    ds_cvdp = ds_cvdp.rename({'npo_pc_mon': 'npo',
                              'pdo_timeseries_mon': 'pdo'})
    times = pd.date_range('1920-01', '2016-01', freq='M')
    ds_cvdp['time'] = times
    ds_cvdp['ensemble'] = ens

    # Detrend all of the climate indices
    ds_cvdp = ds_cvdp.apply(detrend_climate)

    # Create DataFrame to store output from statistical analysis.
    index = np.arange(0, 35, 1)
    columns = ['Slope', 'R Value', 'R Squared', 'P-Value']
    df_enso = pd.DataFrame(index=index, columns=columns)
    df_pdo = pd.DataFrame(index=index, columns=columns)
    df_npo = pd.DataFrame(index=index, columns=columns)
    for idx in np.arange(0, 34, 1):
        # Apply annual filter to the FG_CO2 data and only match up with same
        # legnth time series from CVDP package.
        ts1 = ds_residuals[idx].values
        ts1 = smooth_series(ts1, 12)
        ts1 = ts1[11::]
        ts2 = ds_cvdp['nino34'][idx, 11::].values
        ts3 = ds_cvdp['pdo'][idx, 11::].values
        ts4 = ds_cvdp['npo'][idx, 11::].values
        ensNum = str(ds_residuals[idx].ensemble.values)
        print "Working on Simulation " + ensNum + "..."

        # Run Linear regressions.
        # slope, r, r2, p = linear_regression(ts2, ts1)
        # df_enso['Slope'][idx] = slope
        # df_enso['R Value'][idx] = r
        # df_enso['R Squared'][idx] = r2
        # df_enso['P-Value'][idx] = p

        # slope, r, r2, p = linear_regression(ts3, ts1)
        # df_pdo['Slope'][idx] = slope
        # df_pdo['R Value'][idx] = r
        # df_pdo['R Squared'][idx] = r2
        # df_pdo['P-Value'][idx] = p

        # slope, r, r2, p = linear_regression(ts4, ts1)
        # df_npo['Slope'][idx] = slope
        # df_npo['R Value'][idx] = r
        # df_npo['R Squared'][idx] = r2
        # df_npo['P-Value'][idx] = p

        # autocorr_plot(ts1, ts2, ts3, ts4, ensNum)
        # linear_regression(ts1, ts2, ts3, ts4, ensNum)
        seaborn_jointplot(ts1, ts2, ensNum)
    #df_enso.to_csv('smoothed_fgco2_vs_enso')
    #df_pdo.to_csv('smoothed_fgco2_vs_pdo')
    #df_npo.to_csv('smoothed_fgco2_vs_npo')

if __name__ == '__main__':
    main()
