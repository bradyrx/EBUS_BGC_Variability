"""
Create NPGO Index
Author: Riley X. Brady
Date: 10/05/2017

For a given ensemble member, this script computes the NPGO index.

INPUT 1: Str indicating the ensemble member.

Reference:
1. Di Lorenzo, E. and N. Mantua, 2016: Multi-year persistence of the 2014/15 
North Pacific marine heatwave. Nature Climate Change, 6(11) 1042-+, 
doi:10.1038/nclimate3082. 
2. Joh, Y. and E. Di Lorenzo: Increasing coupling between NPGO and PDO leads 
to prolonged marine heatwaves in the Northeast Pacific. Geophysical Research 
Letters, in review.
3. Personal Communication with Manu (via email)
"""
import numpy as np
import pandas as pd
import xarray as xr
import esmtools as et
from eofs.xarray import Eof
import sys

def main():
    ens = sys.argv[1]
    print("Computing NPGO for ensemble number " + ens + "...")
    filepath = ('/glade/scratch/rbrady/EBUS_BGC_Variability/' +
        'global_residuals/SST/remapped/remapped.SST.' + ens + 
        '.192001-201512.nc')
    print("Global residuals loaded...")
    ds = xr.open_dataset(filepath)
    ds = ds['SST']
    # Slice down to Northeast Pacific domain.
    ds = ds.sel(lat=slice(25, 62), lon=slice(180,250))
    # Take annual JFM means.
    month = ds['time.month']
    JFM = (month <= 3)
    ds_winter = ds.where(JFM).resample('A', 'time')
    # Compute EOF
    coslat = np.cos(np.deg2rad(ds_winter.lat.values))
    wgts = np.sqrt(coslat)[..., np.newaxis]
    solver = Eof(ds_winter, weights=wgts, center=False)
    print("NPGO computed.")
    eof = solver.eofsAsCorrelation(neofs=2)
    variance = solver.varianceFraction(neigs=2)
    # Since you used Manu's method of constructing the EOF with JFM annual
    # averages, you need to reconstruct the monthly index of SSTa by 
    # projecting those values onto the EOF.
    pseudo_pc = solver.projectField(ds, neofs=2, eofscaling=1)
    # Set up as dataset.
    ds = eof.to_dataset()
    ds['pc'] = pseudo_pc
    ds['variance_fraction'] = variance
    ds = ds.rename({'eofs': 'eof'})
    ds = ds.sel(mode=1)
    # Invert to the proper values for the bullseye.
    if ds.sel(lat=45.5, lon=210).eof > 0:
        pass
    else:
        ds['eof'] = ds['eof'] * -1
        ds['pc'] = ds['pc'] * -1
    # Change some attributes for the variables.
    ds['eof'].attrs['long_name'] = 'Correlation between PC and JFM SSTa'
    ds['pc'].attrs['long_name'] = 'Principal component for NPGO'
    # Add a description of methods for clarity.
    ds.attrs['description'] = 'Second mode of JFM SSTa variability over 25-62N and 180-110W.'
    ds.attrs['anomalies'] = 'Anomalies were computed by removing the ensemble mean at each grid cell.'
    ds.attrs['weighting'] = ('The native grid was regridded to a standard 1deg x 1deg (180x360) grid.' +
                             'Weighting was computed via the sqrt of the cosine of latitude.')
    print("Saving to netCDF...")
    ds.to_netcdf('/glade/p/work/rbrady/NPGO/NPGO.' + ens + '.1920-2015.nc')

if __name__ == '__main__':
    main()
