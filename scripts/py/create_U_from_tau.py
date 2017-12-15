"""
Creates regional U10 on the ocean grid from TAUX and TAUY, using the conversion function from Nikki's 2007 paper.

I'm aware this is embarassingly parallel, but .apply() in xarray doesn't seem to be parallelizing it. Perhaps this is better off a Matlab script with parfor loops. I used .apply() and it seemed ~20min per simulation and wasn't coming out with the right answers. This will do for now.

INPUT 1: 'TAU' or 'TAU2' to create U or U2 for regressions. 
INPUT 2: Str for ensemble number.
INPUT 3: Identifier for upwelling system.
"""
import numpy as np
import xarray as xr
import sys
import os
from esmtools.physics import stress_to_speed

def open_ebus_variable(v, en, eb):
    """
    Opens the ensemble member dataset that has been extracted already.
    """
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + v + '/' + eb + '/' + v + '.' + en +
                '.' + eb + '.192001-201512.nc')
    ds = xr.open_dataset(filepath)
    return ds

def main():
    tau_type  = sys.argv[1]
    ens = sys.argv[2]
    ebu = sys.argv[3]
    if tau_type.lower() == 'tau':
        x = open_ebus_variable('TAUX', ens, ebu)
        y = open_ebus_variable('TAUY', ens, ebu)
        name = 'U'
    elif tau_type.lower() == 'tau2':
        x = open_ebus_variable('TAUX2', ens, ebu)
        y = open_ebus_variable('TAUY2', ens, ebu)
        name = 'U2'
    else:
        raise ValueError("Incorrect input. Try either 'TAU' or 'TAU2'")
    _ = np.zeros([x['nlat'].size, x.nlon.size, x.time.size])
    _[:] = np.nan
    ds = xr.DataArray(_, dims=['nlat','nlon','time'], coords=[x.nlat, x.nlon, x.time])
    for i in range(ds.nlat.size):
        for j in range(ds.nlon.size):
            if tau_type.lower() == 'tau':
                xtemp = x['TAUX'].isel(nlat=i, nlon=j)
                ytemp = y['TAUY'].isel(nlat=i, nlon=j)
            else:
                xtemp = x['TAUX2'].isel(nlat=i, nlon=j)
                ytemp = y['TAUY2'].isel(nlat=i, nlon=j)
            if xtemp.min().isnull():
                continue
            else:
                utemp = stress_to_speed(xtemp, ytemp)
                ds[i,j,:] = utemp
    ds.name = name
    ds = ds.to_dataset()
    # Add back in important coordinates.
    ds['ANGLE'] = x['ANGLE']
    ds['ANGLET'] = x['ANGLET']
    ds['DXT'] = x['DXT']
    ds['DYT'] = x['DYT']
    ds['REGION_MASK'] = x['REGION_MASK']
    ds['TAREA'] = x['TAREA']
    ds['UAREA'] = x['UAREA']
    OUT_DIR = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + name + '/' + ebu + '/')
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    OUT_FILE = (OUT_DIR + name + '.' + ens + '.' + ebu + '.192001-201512.nc')
    print("Saving " + ens + " to netCDF...")
    ds.to_netcdf(OUT_FILE)

if __name__ == '__main__':
    main()
