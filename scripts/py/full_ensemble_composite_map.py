"""
Full Ensemble Composite Map
---------------------------
Author: Riley X. Brady
Date: Oct. 16th, 2017

This script performs a composite analysis for the whole ensemble with relation
to EOF modes of CO2 flux in the major EBUS. The output is a netCDF file for
the given system and mode (and variable to composite) with a map of the 
positive composite, negative composite, and neutral composite. Also included
is a count of occurences of the given positive/negative/neutral event for each
month.

NOTE: This script is set up for the North Pacific right now. Need to add 
domains for composites for other systems.

NOTE: Currently, this script is set up to work on residuals. This is a helpful
picture, because it isn't biased by the time of year. The residuals are simply
deviations from the normal seasonal cycle and anthropogenic trend. It can be
modified later to include raw output.

NOTE: You have to make sure you have generated global residuals first and then
remapped them (using the shell scripts in the project folder).

NOTE: This is set up to deal with EOF modes of CO2 flux in the EBUS. It can be
modified to also work with NPGO composites, etc.

INPUT 1: Str for EBUS ('CalCS', 'BenCS', 'CanCS', 'HumCS')
INPUT 2: Int for mode number (Which EOF are you compositing?)
INPUT 3: Str for variable to composite ('SSH', 'SST', etc.)
"""
import glob
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr
from scipy import signal

def composite_domain(ebus):
    """
    Returns latitude and longitude coordinates for slicing out the composite
    domain.
    """
    if ebus == 'CalCS':
        x0 = 145
        x1 = 260
        y0 = -10
        y1 = 60
    else:
        raise Exception("Need to add composite domain for other EBU's.")
    return x0, x1, y0, y1

def xarray_month_count(time_index, name):
    """
    Takes in a time-varying field with ensemble members after filtering for the
    two-sigma or whatever significance bounds. Converts these into a 
    DataArray with month dimension 1-12 and values for the number of pos/neg/
    neutral events for each month.
    """
    stacked_months = time_index.stack(points=['ensemble','time']) \
                               .dropna('points')['time.month']
    df = stacked_months.to_dataframe()
    df = df.groupby('month').size()
    df = df.to_xarray()
    df.name = name
    return df

def main():
    EBU = sys.argv[1]
    MODE = int(sys.argv[2])
    VAR = sys.argv[3]
    # Load in the region's EOF netCDF.
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/regional_EOFs/' +
                EBU + '/FG_ALT_CO2/')
    filename = 'FG_ALT_CO2.EOF.192001-201512.nc'
    ds = xr.open_dataset(filepath + filename)
    ds = ds.sel(mode=MODE)
    ds = ds['pc']
    # Detrend to avoid issues with sigma classification.
    ds = ds.to_dataset().apply(signal.detrend)
    ds = ds['pc']
    # 2 Sigma threshold
    # CHANGE THIS IF YOU WANT 1 SIGMA or 3 SIGMA, etc.
    two_sigma = ds.std() * 2 
    
    # Load in Residual data
    if VAR == 'curl':
        filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/' +
                    VAR + '/')
    else:    
        filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/' + 
                    VAR + '/remapped/')
    ds_var = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
    ds_var = ds_var[VAR]
    ds_var['time'] = pd.date_range('1920-01', '2016-01', freq='M')
    # Slice out composite domain.
    x0, x1, y0, y1 = composite_domain(EBU)
    ds_var = ds_var.sel(lat=slice(y0, y1), lon=slice(x0, x1))
    # Time index for seeing when these events occur.
    pos_time_index = ds.where(ds >= two_sigma, drop=True)
    neg_time_index = ds.where(ds <= two_sigma*-1, drop=True)
    neu_time_index = ds.where( (ds < two_sigma) & (ds > two_sigma*-1), drop=True)
    # Months when events occur.
    pos_months = xarray_month_count(pos_time_index, 'pos_months')
    neg_months = xarray_month_count(neg_time_index, 'neg_months')
    neu_months = xarray_month_count(neu_time_index, 'neu_months')
    # Actual composite map
    pos_composite = ds_var.where(ds >= two_sigma).mean('ensemble').mean('time')
    neg_composite = ds_var.where(ds <= two_sigma*-1).mean('ensemble').mean('time')
    neu_composite = ds_var.where( (ds < two_sigma) & (ds > two_sigma*-1) ) \
                          .mean('ensemble').mean('time')
    # Rename for dataset
    pos_composite.name = 'pos_composite'
    neg_composite.name = 'neg_composite'
    neu_composite.name = 'neu_composite'
    # Save to netCDF.
    ds = pos_composite.to_dataset()
    ds['neg_composite'] = neg_composite
    ds['neu_composite'] = neu_composite
    ds['pos_months'] = pos_months
    ds['neg_months'] = neg_months
    ds['neu_months'] = neu_months
    directory = ('/glade/p/work/rbrady/EBUS_BGC_Variability/composites/' +
                 EBU + '/' + VAR + '/')
    outfile = VAR + '.residuals.FG_ALT_CO2.composite.EOF' + str(MODE) + '.nc'
    if not os.path.exists(directory):
        os.makedirs(directory)
    ds.to_netcdf(directory + outfile)


if __name__ == '__main__':
    main()
