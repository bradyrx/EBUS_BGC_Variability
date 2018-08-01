"""
Integrate 100m
--------------

Specialty script to integrate over the z_t dimension for DIC and SALT to do the
sDIC decomposition. This relies on first running a shell script that extracts
just the upper 100m for each simulation. There's a way to do this with NCO's 
but it wasn't terribly straight forward.

INPUT 1: Variable (string)
INPUT 2: Ensemble member (int)
"""
import xarray as xr
import sys

ens_str = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
           '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
           '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
            '102', '103', '104', '105']

def main():
    VAR = sys.argv[1]
    ENS = int(sys.argv[2])
    filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' + VAR + 
                '100m_monthly/')
    ds = xr.open_dataset(filepath + VAR + '.' + ens_str[ENS] + '.192001-210012.nc',
                decode_times=False)
    ds = ds[VAR]
    print("Summing over z_w_top...")
    ds = ds.sum('z_w_top')
    ds.name = (VAR + '_int100m')
    print("Saving " + VAR + " to netCDF...")
    outdir = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' + VAR + 
              '_int100m_monthly/')
    filename = (VAR + '_int100m.' + ens_str[ENS] + '.192001-210012.nc') 
    ds.to_dataset().to_netcdf(outdir + filename)

if __name__ == '__main__':
    main()
