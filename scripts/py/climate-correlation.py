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
    df = pd.DataFrame({'PDO':climateData,
                       'FG_CO2':carbonData})
    fig = plt.figure(figsize=(6,6))
    with sns.axes_style("white"):
        sns.jointplot(x='PDO', y='FG_CO2', data=df,
                      kind='reg', space=0, color='k')
        plt.savefig('smoothed_jointplot_PDO_' + ensNum + '.png', dpi=1000,
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

def drop_ensemble_dim(ds, x):
    ds[x] = (('nlat', 'nlon'), ds[x][0])
    return ds

def main():
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/FG_CO2/'
    ds = xr.open_mfdataset(fileDir + '*.nc', concat_dim='ensemble')
    # Reduce ensemble dimension for coordinates.
    ds = drop_ensemble_dim(ds, 'DXT')
    ds = drop_ensemble_dim(ds, 'TAREA')
    ds = drop_ensemble_dim(ds, 'REGION_MASK')
    ds = drop_ensemble_dim(ds, 'TLAT')
    ds = drop_ensemble_dim(ds, 'TLONG')
    del ds['DYT']
    del ds['ANGLET']
    # Convert DXT to kilometers.
    ds['DXT'] = ds['DXT'] / 100 / 1000
    # Filter out latitude to Chavez bounds.
    ds = ds.where(ds['TLAT'] >= 34).where(ds['TLAT'] <= 44)
    # Create a masked array for DXT since it doesn't follow the same NaN
    # structure as the co2/region_mask output.
    co2 = ds['FG_CO2'][0,0]
    co2 = np.ma.array(co2, mask=np.isnan(co2))
    # Apply mask to DXT and replace in dataset
    dxt_dat = ds['DXT']
    dxt_dat = np.ma.array(dxt_dat, mask=np.isnan(co2))
    ds['DXT'] = (('nlat','nlon'), dxt_dat)
    # Remove rows that don't have a coastline in them (helps for dist2coast)
    regmask = ds['REGION_MASK']
    counter = 0
    for row in regmask:
        conditional = 0 in row.values
        if conditional == False:
            ds['DXT'][counter, :] = np.nan
        counter += 1
    # Now create a cumulative sum of DXTs. Have to use masked array so there
    # isn't any issue with summing across NaNs.
    x = ds['DXT'].values
    x_masked = np.ma.array(x, mask=np.isnan(x))
    dxt_cum = np.cumsum(x_masked[:, ::-1], axis=1)[:, ::-1]
    ds['DXT_Cum'] = (('nlat','nlon'), dxt_cum)
    # Filter to 800km offshore.
    ds = ds.where(ds['DXT_Cum'] <= 800)

    # + - + - + Post-Filter Computations + - + - + 
    # Subtract out the ensemble mean from all members (create residuals)
    # ds_residuals is now the residuals of FG_CO2. It is a DataArray.
    ds_residuals = ds['FG_CO2'] - ds['FG_CO2'].mean(dim='ensemble')

    # Area-weighting. ds_resiudals is now the area-weighted average time series.
    ds_residuals = ((ds_residuals * ds['TAREA'])
                    .sum(dim='nlat').sum(dim='nlon'))/ds['TAREA'].sum()

    # Load in CVDP data.
    fileDir = '/glade/p/work/rbrady/cesmLE_CVDP/extracted_vars/'
    ds_cvdp = xr.open_mfdataset(fileDir + '*.nc', decode_times=False,
                                concat_dim='ensemble')
    ds_cvdp = ds_cvdp.rename({'npo_pc_mon': 'npo',
                              'pdo_timeseries_mon': 'pdo'})
    times = pd.date_range('1920-01', '2016-01', freq='M')
    ds_cvdp['time'] = times

    # Detrend all of the climate indices
    ds_cvdp = ds_cvdp.apply(detrend_climate)

    # + - + - + - STATISTICAL ANALYSIS + - + - + -
    # Create a DataFrame to store correlation analysis on different climate
    # indices.
    index = np.arange(0, 35, 1)
    columns = ['Slope', 'R Value', 'R Squared', 'P-Value']
    df_enso = pd.DataFrame(index=index, columns=columns)
    df_pdo = pd.DataFrame(index=index, columns=columns)
    df_npo = pd.DataFrame(index=index, columns=columns)
    for idx in np.arange(0, 34, 1):
        # Apply annual filter to the FG_CO2 data and only match up with same
        # legnth time series from CVDP package.
        ts1 = ds_residuals[idx].values
        # Apply 12-month rolling mean to the FG_CO2 data.
        ts1 = smooth_series(ts1, 12)
        # Cut off the NaNs on the front end.
        ts1 = ts1[11::]
        # Only compare the same length time series.
        ts2 = ds_cvdp['nino34'][idx, 11::].values
        ts3 = ds_cvdp['pdo'][idx, 11::].values
        ts4 = ds_cvdp['npo'][idx, 11::].values
        print "Working on simulation " + str(idx+1) + " of 35..."
        
        # +++ Create Seaborn stats plots
        ensNum = str(idx)
        seaborn_jointplot(ts1, ts3, ensNum)  

        # +++ Run Linear regressions.
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
    # df_enso.to_csv('smoothed_fgco2_vs_enso')
    # df_pdo.to_csv('smoothed_fgco2_vs_pdo')
    #df_npo.to_csv('smoothed_fgco2_vs_npo')

if __name__ == '__main__':
    main()
