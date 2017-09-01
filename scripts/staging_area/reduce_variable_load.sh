#!/bin/bash
#PBS -A P93300670
#PBS -N reduce_alt_co2
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=16
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 05/25/2017
# Purpose : Quick script to take output from CESM-LENS that has MANY variables embedded, and just pull out the variable and coordinates of interest. 
# This makes it easier to manage when loading a bunch of files into xArray.

MAIN_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/FG_ALT_CO2_monthly

cd ${MAIN_DIR}

ls *.nc | parallel 'echo {}; ncks -v FG_ALT_CO2,TLAT,TLONG,TAREA,ANGLET,DXT,DYT,REGION_MASK {} reduced.{}'
