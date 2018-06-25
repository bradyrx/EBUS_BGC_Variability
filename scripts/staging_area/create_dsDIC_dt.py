"""
Create dsDIC/dt
Author: Riley X. Brady
Date: 05/31/2018
===============

This script takes in DIC and SALT from a simulation and computes the time-rate
of change of salinity-normalized DIC (sDIC). This is probably a one-time use
script for the EBUS BGC Variability paper, but will prove helpful for other
efforts in the future.

I have done some pre-processing here to integrate over the upper 100m for DIC
and SALT for all large ensemble simulations. This is what is being loaded in
to the script.

INPUT 1: (Int) Simulation number (0..33)
"""
import numpy as np
import xarray as xr
import sys

ens_str = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
           '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
           '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
            '102', '103', '104', '105']

def main():
    ENS = int(sys.argv[1])
    DIC_filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/DIC_int100m_monthly/')
    SALT_filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/SALT_int100m_monthly/')
    da1 = xr.open_dataarray(DIC_filepath + 'DIC_int100m.' + ens_str[ENS] +
        '.192001-210012.nc', decode_times=False)
    da2 = xr.open_dataarray(SALT_filepath + 'SALT_int100m.' + ens_str[ENS] +
        '.192001-210012.nc', decode_times=False)
    # Salinity normalize to create sDIC over upper 100m.
    ds = (da1/da2) * 35
    del da1
    del da2
    ds.name = 'sDIC_int100m'
    # Compute gradient to approxmate dsDIC/dt
    print("Computing gradient...")
    ds = ds.stack(points=['nlat','nlon']).groupby('points') \
            .apply(np.gradient).unstack('points')
    # Save to netCDF
    ds.name = 'sDIC_int100m_tendency'
    ds.attrs['Description'] = ('DIC and SALT were integrated over the upper ' +
        '100m for the given simulation and then sDIC was created by taking ' +
        '(DIC/SALT)*35. Then np.gradient was applied to these data to approx.' +
        ' the time rate of change.')
    outdir = ('/glade/scratch/rbrady/EBUS_BGC_Variability/sDIC_int100m_tendency/')
    print("Saving to netCDF...")
    ds.to_dataset().to_netcdf(outdir + 'sDIC_int100m_tendency.' + ens_str[ENS] +
        '.192001-210012.nc')


if __name__ == '__main__':
    main()
