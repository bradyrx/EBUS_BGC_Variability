#!/bin/bash
#PBS -A P93300670
#PBS -N reduce_variable_load
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=1
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 05/25/2017
# Purpose : Quick script to take output from CESM-LENS that has MANY variables embedded, and just pull out the variable and coordinates of interest. 
# This makes it easier to manage when loading a bunch of files into xArray.

VAR=pCO2SURF
MAIN_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly

source `which env_parallel.bash`

cd ${MAIN_DIR}

ls *.nc | env_parallel 'echo {}; ncks -v ${VAR},ULAT,ULONG,UAREA,ANGLE,TLAT,TLONG,TAREA,ANGLET,DXT,DYT,REGION_MASK {} reduced.{}'
