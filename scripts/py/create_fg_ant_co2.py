# Create FG_ANT_CO2 
# Author: Riley X. Brady
# Date: September 14th, 2017
"""
This is not a terribly flexible script. Given an input of an EBUS, it moves to
the folder containing the contemporary CO2 flux (FG_CO2) and the folder 
containing the natural CO2 flux (FG_ALT_CO2) and subtracts them to derive a new
timeseries called FG_ANT_CO2, the anthropogenic perturbation of CO2. 
"""

# INPUT 1 : Ensemble member number
# INPUT 2 : EBUS identifier (CalCS, BenCS, HumCS, CanCS)
import os
import sys
import numpy as np
import pandas as pd
import xarray as xr

def main():
    ensNum = sys.argv[1]
    EBUS = sys.argv[2]
    conDir = ('/glade/u/home/rbrady/work/EBUS_BGC_Variability/FG_CO2/' + EBUS +  
    '/')
    conFile = 'FG_CO2.' + ensNum + '.' + EBUS + '.192001-201512.nc'
    natDir = ('/glade/u/home/rbrady/work/EBUS_BGC_Variability/FG_ALT_CO2/' + 
    EBUS + '/')
    natFile = 'FG_ALT_CO2.' + ensNum + '.' + EBUS + '.192001-201512.nc'
    ds_con = xr.open_dataset(conDir + conFile)
    ds_nat = xr.open_dataset(natDir + natFile)
    ds_ant = ds_con['FG_CO2'] - ds_nat['FG_ALT_CO2']
    ds_ant.name = 'FG_ANT_CO2'
    ds_ant = ds_ant.to_dataset()
    ds_ant['ANGLET'] = ds_con['ANGLET']
    ds_ant['DXT'] = ds_con['DXT']
    ds_ant['DYT'] = ds_con['DYT']
    ds_ant['REGION_MASK'] = ds_con['REGION_MASK']
    ds_ant['TAREA'] = ds_con['TAREA']
    ds_ant.attrs['carbon flux units'] = 'mol/m2/yr'
    ds_ant.attrs['area units'] = 'm2'
    ds_ant.attrs['long name'] = 'anthropogenic sea-air carbon flux'
    newFile = 'FG_ANT_CO2.' + ensNum + '.' + EBUS + '.192001-201512.nc'
    directory = ('/glade/p/work/rbrady/EBUS_BGC_Variability/FG_ANT_CO2/' + 
                EBUS + '/')
    if not os.path.exists(directory):
        os.makedirs(directory)
    ds_ant.to_netcdf(directory + newFile)

if __name__ == '__main__':
    main()
    
