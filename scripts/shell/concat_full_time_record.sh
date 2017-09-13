#!/bin/bash
#PBS -A P93300670
#PBS -N concat_full_record
#PBS -l walltime=02:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=1
#PBS -m abe
# Author : Riley X. Brady
# Date : 05/31/2017
# Purpose : Given a variable, will concatenate every BGC member from 1920-2100 and store away in scratch.
# This is helpful for reading into xarray and messing around with from there. 
# Notes : 
# - Cannot easily do in parallel due to all the differences between ensemble member file structure.

VAR=FG_CO2
INPUT_DIR=/glade/p/cesmLE/CESM-CAM5-BGC-LE/ocn/proc/tseries/monthly/${VAR}
OUTPUT_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly

mkdir -p ${OUTPUT_DIR}

# Loop is for known BGC output. This is used because known ensemble members are split up differently.
for n in {001,002,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,101,102,103,104,105}
do
    echo "Working on file ${n}..."
    if [ ${n} == 001 ]
    then
        # Dealing with the fact that s001 begins with 1850. Need to turn it into 1920, then delete it at the end of the whole process.
        temp_file=${INPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.185001-200512.nc
        ncks -F -d time,841, ${temp_file} ${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
        histFile=${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
    else
        histFile=${INPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
    fi

    if [ ${n} == 034 ] || [ ${n} == 035 ] || [ ${n} == 101 ] || [ ${n} == 102 ] || [ ${n} == 103 ] || [ ${n} == 104 ] || [ ${n} == 105 ]
    then
        futFile=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-210012.nc
        ncrcat ${histFile} ${futFile} ${OUTPUT_DIR}/${VAR}.${n}.192001-210012.nc
    else
        fut1=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-208012.nc
        fut2=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.208101-210012.nc
        ncrcat ${histFile} ${fut1} ${fut2} ${OUTPUT_DIR}/${VAR}.${n}.192001-210012.nc
    fi 

    # Get rid of extraneous ens001 historical file
    if [ ${n} == 001 ]
    then
        rm ${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.001.pop.h.${VAR}.192001-200512.nc
    fi    
done
