#!/bin/bash
#PBS -A P93300670
#PBS -N WVEL-fullseries
#PBS -l walltime=06:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=1
#PBS -m abe

# Author : Riley X. Brady
# Date : 01/11/2018
#
# Given dimensions (nlat/nlon) this will slice out a specified depth profile
# of a given variable.
#
# CalCS : nlon (226,265); nlat (265,310)
# HumCS : nlon (266,293); nlat (115,187)
# CanCS : nlon (8,35);  nlat (254,284)
# BenCS : nlon (36,53); nlat (92,127)
#
VAR=DIC
INPUT_DIR=/glade/p/cesmLE/CESM-CAM5-BGC-LE/ocn/proc/tseries/monthly/${VAR}
OUTPUT_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly_depth
x0=265 # Zero-indexed nlon/nlat coordinates for the region of the globe sliced.
x1=310
y0=226
y1=265
DEPTH_VAR=z_t
D0=0 # Zero-indexed depth layer for slicing.
D1=5

mkdir -p ${OUTPUT_DIR}

# Loop is for known BGC output.
for n in {001,002,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,101,102,103,104,105}
do
    echo "Working on file ${n}..."
    if [ ${n} == 001 ]
    then
        temp_file=${INPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.185001-200512.nc
        ncks -d time,840, -d ${DEPTH_VAR},${D0},${D1} -d nlon,${x0},${x1} -d nlat,${y0},${y1} -v ${VAR},TAREA ${temp_file} ${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
        histFile=${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
    else
        temp_file=${INPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
        ncks -d ${DEPTH_VAR},${D0},${D1} -d nlon,${x0},${x1} -d nlat,${y0},${y1} -v ${VAR},TAREA ${temp_file} ${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
        histFile=${OUTPUT_DIR}/b.e11.B20TRC5CNBDRD.f09_g16.${n}.pop.h.${VAR}.192001-200512.nc
    fi

    if [ ${n} == 034 ] || [ ${n} == 035 ] || [ ${n} == 101 ] || [ ${n} == 102 ] || [ ${n} == 103 ] || [ ${n} == 104 ] || [ ${n} == 105 ]
    then
        temp_file=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-210012.nc
        ncks -d ${DEPTH_VAR},${D0},${D1} -d nlon,${x0},${x1} -d nlat,${y0},${y1} -v ${VAR},TAREA ${temp_file} ${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-210012.nc
        futFile=${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-210012.nc
        ncrcat ${histFile} ${futFile} ${OUTPUT_DIR}/${VAR}.${n}.192001-210012.nc
        rm ${histFile} ${futFile}
    else
        temp1=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-208012.nc
        ncks -d ${DEPTH_VAR},${D0},${D1} -d nlon,${x0},${x1} -d nlat,${y0},${y1} -v ${VAR},TAREA ${temp1} ${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-208012.nc
        fut1=${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.200601-208012.nc
        temp2=${INPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.208101-210012.nc
        ncks -d ${DEPTH_VAR},${D0},${D1} -d nlon,${x0},${x1} -d nlat,${y0},${y1} -v ${VAR},TAREA ${temp2} ${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.208101-210012.nc
        fut2=${OUTPUT_DIR}/b.e11.BRCP85C5CNBDRD.f09_g16.${n}.pop.h.${VAR}.208101-210012.nc
        ncrcat ${histFile} ${fut1} ${fut2} ${OUTPUT_DIR}/${VAR}.${n}.192001-210012.nc
        rm ${histFile} ${fut1} ${fut2}
    fi
done

