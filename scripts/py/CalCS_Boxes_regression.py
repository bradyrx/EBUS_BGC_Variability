"""
CalCS Boxes Regression
----------------------
A quick script to run correlations/regressions between a sub-box of the CalCS
(onshore/offshore) and some climate variable. This is for the CO2 flux decomp.

The onshore/offshore variables have to have been generated via the
create_CalCS_subbox.py script.

INPUT 1: Location (onshore/offshore)
INPUT 2: VARX
INPUT 3: VARY
INPUT 4: LAG (int)
INPUT 5: SMOOTH (int)
"""
import sys
import os
import glob
import numpy as np
import xarray as xr
import esmtools as et

def load_residuals(b, v):
    """
    Loads in the area-weighted residuals for the given box (b) [onshore/offshore]
    and the given variable (v).
    """
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/CalCS_Boxes/' +
                b.lower() + '/' + v + '/CalCS.' + v + '.' + b.lower() + '.residuals.nc')
    da = xr.open_dataarray(filepath)
    da.name = v
    return da

def main():
    LOC = sys.argv[1]
    VARX = sys.argv[2]
    VARY = sys.argv[3]
    LAG = int(sys.argv[4])
    SMOOTH = int(sys.argv[5])
    print("Working on " + VARX + " predicting " + VARY + " in the " +
         LOC.lower() + " region of the CalCS with " + str(LAG) +
         " mo. lag and " + str(SMOOTH) + " mo. smoothing...")
    # Load in the X variable.
    if VARX == 'NPGO':
        """
        This was a custom EOF procedure, so the NC files are very different
        from the way Adam Phillips set his up.
        """
        filepath = '/glade/p/work/rbrady/EBUS_BGC_Variability/NPGO/'
        ds_x = xr.open_mfdataset(filepath + '*.nc', concat_dim='ensemble')
        ds_x = ds_x['pc']
    else:
        """
        This assumes the variable can be found in Adam Phillip's climate
        diagnostics output. Need to edit this loading if that's not the
        case.
        """
        filepath = '/glade/p/work/rbrady/cesmLE_CVDP/processed/'
        filename = 'cvdp_detrended_BGC.nc'
        ds_x = xr.open_dataset(filepath + filename)
        ds_x = ds_x[VARX.lower()]
        if VARX == 'AMOC':
            # Account for the time dimension labeling.
            ds_x = ds_x.rename({'TIME': 'time'})
    # Load in the Y variable.
    ds_y = load_residuals(LOC, VARY)
    # Resample to annual resolution if dealing with AMOC, since it is only at
    # annual resolution.
    if VARX == 'AMOC':
        ds_y = ds_y.resample(freq='AS', dim='time')
        ds_y['time'] = np.arange(1920, 2016, 1)
    # Smooth if necessary.
    if SMOOTH != 0:
            ds_x = ds_x.rolling(time=SMOOTH).mean().dropna('time')
            ds_y = ds_y.rolling(time=SMOOTH).mean().dropna('time')
    # Combine into one dataset.
    ds_x.name = 'x'
    ds_y.name = 'y'
    ds = ds_x.to_dataset()
    ds['y'] = ds_y
    # Run the correlation (Here can definitely be improved..)
    m, r, p, n = ([] for i in range(4))
    for label, group in ds.groupby('ensemble'):
        """
        Run a simple correlation/regression, but need to check for all of the
        optional lag and smoothing settings.
        Updated to use new esmtools pearsonr which accounts for autocorrelation
        when smoothing.
        """
        if LAG == 0:
            M, _, _, _, _ = et.stats.linear_regression(group.x, group.y)
            R, P, N = et.stats.pearsonr(group.x, group.y)
            m.append(M)
            r.append(R)
            p.append(P)
            n.append(N)
        else:
            M, _, _, _, _ = et.stats.linear_regression(group.x[:-LAG],
                                                       group.y[LAG:])
            R, P, N = et.stats.pearsonr(group.x[:-LAG], group.y[LAG:])
            m.append(M)
            r.append(R)
            p.append(P)
            n.append(N)
    # Set up in dataset.
    ds = xr.Dataset({'m': ('ensemble', m),
                     'r': ('ensemble', r),
                     'p': ('ensemble', p),
                     'n_eff': ('ensemble', n)})
    print("Finished regional correlations.")
    directory = ('/glade/p/work/rbrady/EBUS_BGC_Variability/CalCS_Boxes/' +
                LOC.lower() + '/regression_results/' + VARY + '/' + VARX + '/')
    if not os.path.exists(directory):
        os.makedirs(directory)
    if SMOOTH != 0: # Save with smoothing in file name.
        out_file = (directory + VARX + '.' + VARY + '.' + LOC.lower() + '.smoothed' +
                    str(SMOOTH) + '.regression.lag' +
                    str(LAG) + '.nc')
    else:
        out_file = (directory + VARX + '.' + VARY + '.' + LOC.lower() +
                    '.unsmoothed.regression.lag' +
                    str(LAG) + '.nc')
    print("Saving to netCDF...")
    ds.to_netcdf(out_file)

if __name__ == '__main__':
    main()
