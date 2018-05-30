"""
Reconstruct Curl
---------------
Author : Riley X. Brady
Date   : 4/20/2018

I computed the global curl for all members of CESM-LENS a little while back but
only saved them out as a global mean and global residuals. This simply adds the
two back together and saves them in scratch space. With this, I can run the
EBUS_Extraction script to get curl for each region. I want to correlate curl
with ENSO for the HumCS, since some weird results are coming up. Namely, I am 
seeing that sDIC is decreasing a lot during El Nino and upwelling is being 
reduced, but TAUX/TAUY and U are enhancing in the upwelling-favorable direction.

INPUT 1: Ensemble number (int between 0 and 33)
"""
import sys
import os
import xarray as xr

ens_str = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
           '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
           '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
            '102', '103', '104', '105']

def main():
    ENS = int(sys.argv[1])
    print("Reconstructing curl for simulation " + ens_str[ENS] + "...")
    meandir = '/glade/p/work/rbrady/EBUS_BGC_Variability/global_mean/'
    residdir = ('/glade/p/work/rbrady/EBUS_BGC_Variability/global_residuals/' +
                'curl/')
    ds_mean = xr.open_dataset(meandir + 'curl.ensemble_mean.1920-2015.nc')
    ds_resid = xr.open_dataset(residdir + 'residual.curl.' + ens_str[ENS] +
                    '.192001-201512.nc')
    reconstructed = ds_mean + ds_resid
    # Save file out.
    print("Saving netCDF...")
    out_dir = '/glade/scratch/rbrady/EBUS_BGC_Variability/curl_monthly/'
    out_name = 'curl.' + ens_str[ENS] + '.192001-210012.nc'
    reconstructed.to_netcdf(out_dir + out_name)

if __name__ == '__main__':
    main()
