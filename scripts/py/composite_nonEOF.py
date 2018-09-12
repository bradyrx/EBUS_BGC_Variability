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
INPUT 4: Log for whether of not to use remapped version ('True' or 'False')
"""
import glob
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr
import esmtools as et


def composite_domain(ebus):
    """
    Returns latitude and longitude coordinates for slicing out the composite
    domain.
    """
    if ebus == 'HumCS':
        x0 = 100 
        x1 = 300
        y0 = -60
        y1 = 30 
    elif ebus == 'CalCS':
        x0 = 145 
        x1 = 260 
        y0 = -10 
        y1 = 60 
    elif ebus == 'CanCS':
        x0 = 280 
        x1 = 30 
        y0 = -20
        y1 = 60
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
    if MODE == 'NPGO':
        filepath = '/glade/work/rbrady/EBUS_BGC_Variability/NPGO/'
        cvdp = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
        cvdp = cvdp['pc']
    else:
        filepath = '/glade/work/rbrady/cesmLE_CVDP/processed/cvdp_detrended_BGC.nc'
        cvdp = xr.open_dataset(filepath)
        cvdp = cvdp[MODE.lower()]
    # 2 Sigma Threshold
    two_sigma = cvdp.std() * 2
    # Load in residual data.
    if VAR == 'curl':
        filepath = ('/glade/work/rbrady/EBUS_BGC_Variability/global_residuals/' +
                    VAR + '/')
    else:
        if sys.argv[4] == 'True':
            filepath = ('/glade/work/rbrady/EBUS_BGC_Variability/global_residuals/' + 
                        VAR + '/remapped/')
        elif sys.argv[4] == 'False':
            filepath = ('/glade/work/rbrady/EBUS_BGC_Variability/global_residuals/' +
                        VAR + '/')
    ds_var = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble', 
                               decode_times=False)
    ds_var = ds_var[VAR]
    ds_var['time'] = pd.date_range('1920-01', '2016-01', freq='M')
    x0, x1, y0, y1 = composite_domain(EBU)
    if sys.argv[4] == 'True':
        if EBU == 'CanCS':
            ds1 = ds_var.sel(lat=slice(y0, y1), lon=slice(x0, 360))
            ds2 = ds_var.sel(lat=slice(y0, y1), lon=slice(0, x1))
            ds_var = xr.concat([ds1, ds2], dim='lon')
            # Convert to -180 to 180
            new_lon = np.empty((ds_var.lon.values.size))
            for i, val in enumerate(ds_var.lon.values):
                if val > 100:
                    new_lon[i] = val - 360
                else:
                    new_lon[i] = val
            ds_var['lon'] = new_lon
        else:
            ds_var = ds_var.sel(lat=slice(y0, y1), lon=slice(x0, x1))
    else:
        try:
            ds_var['TLONG'] = ds_var['TLONG'].isel(ensemble=0)
            ds_var['TLAT'] = ds_var['TLAT'].isel(ensemble=0)
        except:
            pass
        a, c = et.filtering.find_indices(ds_var['TLAT'].values, ds_var['TLONG'].values,
                                         y0, x0)
        b, d = et.filtering.find_indices(ds_var['TLAT'].values, ds_var['TLONG'].values,
                                         y1, x1)
        ds_var = ds_var.isel(nlat=slice(a, b), nlon=slice(c, d))
    # Time index for seeing when these events occur.
    print("Indexing time...")
    pos_time_index = cvdp.where(cvdp >= two_sigma, drop=True)
    neg_time_index = cvdp.where(cvdp <= two_sigma*-1, drop=True)
    neu_time_index = cvdp.where( (cvdp < two_sigma) & (cvdp > two_sigma*-1), drop=True)
    # Months when events occur.
    pos_months = xarray_month_count(pos_time_index, 'pos_months')
    neg_months = xarray_month_count(neg_time_index, 'neg_months')
    neu_months = xarray_month_count(neu_time_index, 'neu_months')
    # Actual composite map.
    print("Mapping composites...")
    pos_composite = ds_var.where(cvdp >= two_sigma).mean('ensemble').mean('time')
    neg_composite = ds_var.where(cvdp <= two_sigma*-1).mean('ensemble').mean('time')
    neu_composite = ds_var.where( (cvdp < two_sigma) & (cvdp > two_sigma*-1) ) \
                 .mean('ensemble').mean('time')
    # Rename for dataset.
    pos_composite.name = 'pos_composite'
    neg_composite.name = 'neg_composite'
    neu_composite.name = 'neu_composite'
    # Save to netCDF.
    print("Creating dataset...")
    ds = pos_composite.to_dataset()
    ds['neg_composite'] = neg_composite
    ds['neu_composite'] = neu_composite
    ds['pos_months'] = pos_months
    ds['neg_months'] = neg_months
    ds['neu_months'] = neu_months
    try:
        ds = ds.squeeze()
    except:
        pass
    print("Saving to netCDF...")
    directory = ('/glade/work/rbrady/EBUS_BGC_Variability/composites/' +
                 EBU + '/' + VAR + '/')
    if sys.argv[4] == 'True':
        outfile = VAR + '.remapped.composite.' + str(MODE) + '.nc'
    else:
        outfile = VAR + '.native.composite.' + str(MODE) + '.nc'
    if not os.path.exists(directory):
        os.makedirs(directory)
    ds.to_netcdf(directory + outfile)

if __name__ == '__main__':
    main()
