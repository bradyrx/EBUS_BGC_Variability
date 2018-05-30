"""
Composite Non-EOF
-----------------
Author : Riley X. Brady
Date   : 4/20/2018

This is based on the other compositing script, which was used to composite with
FG_CO2 EOFs in the CalCS. This is more generalized for a composite on any mode
of climate variability. This was made to look at HumCS composites for ENSO to
figure out what's going on. Can be adapted to include other domains.

NOTE: Make sure to have global residuals remapped for this.

INPUT 1: Str for EBUS ('HumCS', ...)
INPUT 2: Str for climate mode ('NINO3', ...)
INPUT 3: Str for composite variable ('SST', 'SSH', ...)
"""
import glob
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr

def composite_domain(ebus):
    """
    Returns latitude and longitude coordinates for slicing out the composite
    domain.
    """
    if ebus == 'HumCS':
        x0 = 180
        x1 = 300
        y0 = -60
        y1 = 15
    else:
        raise Exception("Need to add composite domain for other EBUS.")
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
    MODE = sys.argv[2]
    VAR = sys.argv[3]
    # Load in CVDP
    filepath = '/glade/p/work/rbrady/cesmLE_CVDP/processed/cvdp_detrended_BGC.nc'
    cvdp = xr.open_dataset(filepath)
    cvdp = cvdp[MODE.lower()]
    # 2 Sigma Threshold
    two_sigma = cvdp.std() * 2
    # Load in residual data.
    if VAR == 'curl':
        filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/global_residuals/' +
                    VAR + '/')
    else:
        filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/global_residuals/' + 
                    VAR + '/remapped/')
    ds_var = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
    ds_var = ds_var[VAR]
    ds_var['time'] = pd.date_range('1920-01', '2016-01', freq='M')
    x0, x1, y0, y1 = composite_domain(EBU)
    ds_var = ds_var.sel(lat=slice(y0, y1), lon=slice(x0, x1))
    # Time index for seeing when these events occur.
    pos_time_index = cvdp.where(cvdp >= two_sigma, drop=True)
    neg_time_index = cvdp.where(cvdp <= two_sigma*-1, drop=True)
    neu_time_index = cvdp.where( (cvdp < two_sigma) & (cvdp > two_sigma*-1), drop=True)
    # Months when events occur.
    pos_months = xarray_month_count(pos_time_index, 'pos_months')
    neg_months = xarray_month_count(neg_time_index, 'neg_months')
    neu_months = xarray_month_count(neu_time_index, 'neu_months')
    # Actual composite map.
    pos_composite = ds_var.where(cvdp >= two_sigma).mean('ensemble').mean('time')
    neg_composite = ds_var.where(cvdp <= two_sigma*-1).mean('ensemble').mean('time')
    neu_composite = ds_var.where( (cvdp < two_sigma) & (cvdp > two_sigma*-1) ) \
                 .mean('ensemble').mean('time')
    # Rename for dataset.
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
    outfile = VAR + '.residuals.FG_CO2.composite.' + VAR + '.'  + str(MODE) + '.nc'
    if not os.path.exists(directory):
        os.makedirs(directory)
    ds.to_netcdf(directory + outfile)

if __name__ == '__main__':
    main()
