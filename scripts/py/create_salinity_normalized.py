"""
Simple script to convert DIC or ALK to sDIC or sALK. This is to make sure that the regressions done in CO2 flux decomposition are not from converted residuals, but from raw sDIC.

INPUT 1: 'DIC' or 'ALK'
INPUT 2: Str for ensemble number.
INPUT 3: Identifier for upwelling system.
"""
import xarray as xr
import sys
import os

def open_ebus_variable(v, en, eb):
    """
    Opens the ensemble member dataset that has been extracted already.
    """
    filepath = ('/glade/p/work/rbrady/EBUS_BGC_Variability/' + v + '/' + eb + '/' + v + '.' + en +
                '.' + eb + '.192001-201512.nc')
    ds = xr.open_dataset(filepath)
    return ds

def main():
    var = sys.argv[1]
    ens = sys.argv[2]
    ebu = sys.argv[3]
    salt = open_ebus_variable('SALT', ens, ebu)
    ds = open_ebus_variable(var, ens, ebu)
    ds['s' + var] = (ds[var]/salt['SALT'])*35
    del ds[var]
    OUT_DIR = ('/glade/p/work/rbrady/EBUS_BGC_Variability/s' + var + '/' + ebu + '/')
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    OUT_FILE = (OUT_DIR + 's' + var + '.' + ens + '.' + ebu + '.192001-201512.nc')
    print("Saving " + ens + " to netCDF...")
    ds.to_netcdf(OUT_FILE)

if __name__ == '__main__':
    main()
