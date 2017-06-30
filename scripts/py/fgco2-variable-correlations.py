# Author  : Riley X. Brady
# Date    : 06/29/2017
"""
Desc: Use this script to correlated some predictor variable (that is NOT a
climate index timeseries from the CVDP package; e.g. pCO2) to FG_CO2 anomalies in the four
EBUS. Currently, by default, the script applies annual smoothing to both the
FG_CO2 time series and the predictor variable. It then runs a linear regression
on the two, producing a CSV output with results, as well as seaborn dist_plots
for every case. 

Prep Workflow: Make sure that you have already gone through the routine of
processing the variables of interest. You should first run the shell scripts to
concatenate the CESM-LE output into a monthly resolution time series over
1920-2100 and then strip the netCDF down to a few variables of importance. Then
you run the EBUS_Extraction script to create new netCDF files over each of the
EBUS. Lastly, you run the generate_residuals.py script to create residuals,
which are read into this script.
"""
# INPUTS #
# INPUT 1 : A string of which EBU to work on
# INPUT 2 : A string of which variable to correlate FGCO2 anomalies to.
# INPUT 3 : True/False of whether or not to run the regression visualization.
import os
import glob
import sys
# Numerics
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
# Visualization
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)
from constants import *

def area_weight(ds):
    """
    Takes in a dataset and simply area-weights it, forcing it into a
    timeseries. Currently assumes the names of dimensions and area. Can be
    modified later to fix this.
    """
    ds = ((ds * ds['TAREA']).sum(dim='nlat').sum(dim='nlon'))/ds['TAREA'].sum()
    return ds

def smooth_series(x, length=12):
    return pd.rolling_mean(x, length)

def linear_regression(df, idx, x, y):
    """
    Simple linear regression, with x as the predictor (generally NOT the CO2
    flux anomalies) and y as the dependent variable (generally FG_CO2). Input
    is a pandas dataframe that will store the results.
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    df['Slope'][idx] = slope
    df['R Value'][idx] = r_value
    df['R Squared'][idx] = r_value**2
    df['P-Value'][idx] = p_value
    return df

def main():
    EBU = sys.argv[1]
    VAR = sys.argv[2]
    print "Correlating FG_CO2 with {} in the {}".format(VAR, EBU)
    # + + + FG_CO2
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/FG_CO2/' + EBU + \
            '/filtered_residuals/'
    ds_fgco2 = xr.open_dataset(fileDir + EBU.lower() +
                               '-FG_CO2-residuals-chavez-800km.nc')
    ds_fgco2 = area_weight(ds_fgco2)
    # + + + OTHER VARIABLE
    fileDir = '/glade/p/work/rbrady/EBUS_BGC_Variability/' + VAR + '/' + \
            EBU + '/filtered_residuals/'
    ds_var = xr.open_dataset(fileDir + EBU.lower() + '-' + VAR + \
                             '-residuals-chavez-800km.nc')
    ds_var = area_weight(ds_var)
    # + + + STATISTICAL ANALYSIS
    columns = ['Slope', 'R Value', 'R Squared', 'P-Value']
    df_corr = pd.DataFrame(index=ens, columns=columns)
    for idx in np.arange(0, 34, 1):
        print "Working on Simulation {} of 34".format(idx+1)
        dat_var = ds_var[VAR][idx].values
        dat_var = smooth_series(dat_var)
        dat_var = dat_var[11::]
        dat_fgco2 = ds_fgco2['FG_CO2'][idx].values
        dat_fgco2 = smooth_series(dat_fgco2)
        dat_fgco2 = dat_fgco2[11::]
        df_corr = linear_regression(df_corr, idx, dat_var, dat_fgco2)
        directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
                'data/processed/' + EBU.lower() + '/'
    df_corr.to_csv(directory + 'smoothed_fgco2_vs_smoothed_' + VAR + '_' + EBU)
    # + + + Make Seaborn postage plot
    """
    This is the bottleneck and you decide whether or not it is run by
    "True/False" conditional of the third input. If "True", this runs and
    produces a big subplot of regressions. 
    """
    conditional = sys.argv[3]
    if conditional == "True":
        fig, axes = plt.subplots(figsize=(16,16), nrows=6, ncols=6)
        st = fig.suptitle(EBU + ' ' + VAR + '-FG_CO2 Anomaly Regression (1920-2015)',
                          fontsize=30)
        counter = 0
        for ax in axes.flat:
            print "Visualizing {} of 36...".format(str(counter+1))
            if counter >= 34:
                fig.delaxes(ax)
            else:
                dat_var = ds_var[VAR][counter].values
                dat_var = smooth_series(dat_var)
                dat_var = dat_var[11::]
                dat_co2 = ds_fgco2['FG_CO2'][counter].values
                dat_co2 = smooth_series(dat_co2)
                dat_co2 = dat_co2[11::]
                slope,intercept,r,r2,p = stats.linregress(dat_var,dat_co2)
                df = pd.DataFrame(dict(variable=dat_var, FG_CO2=dat_co2))
                sns_ax = sns.regplot(x='variable', y='FG_CO2', data=df,
                                     color=colors[EBU],
                                     line_kws=dict(color='k', linewidth=1),
                                     ax=ax)
                xlim1, xlim2 = sns_ax.get_xlim()
                ylim1, ylim2 = sns_ax.get_ylim()
                sns_ax.grid('on')
                if VAR == 'pCO2SURF':
                    sns_ax.text(xlim1+0.5, ylim2-0.15, 'S' + ens[counter], fontsize=14,
                                bbox=dict(facecolor='w', edgecolor='k', alpha=1))
                    sns_ax.text(xlim2-4, ylim2-0.15, 'r=' + str(r.round(2)), fontsize=14)
                else:
                    sns_ax.text(xlim1+0.25, ylim2-0.25, 'S' + ens[counter],
                                fontsize=14, bbox=dict(facecolor='w',
                                                       edgecolor='k', alpha=1))
                    sns_ax.text(xlim2-2, ylim2-0.25, 'r=' + str(r.round(2)),
                                fontsize=14)
                sns_ax.set_xlabel(VAR)
            counter += 1
        fig.tight_layout(pad=3)
        fig.subplots_adjust(top=0.90)
        st.set_y(0.95)
        directory = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
                'reports/figs/' + EBU.lower() + '/regression_plots/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(directory + 'smoothed_FGCO2_vs_smoothed_' + VAR + \
                    'regression_subplots.png')

if __name__ == '__main__':
    main()
