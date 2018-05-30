#!/bin/bash
#PBS -A P93300670
#PBS -N mean_and_resid_HMXL
#PBS -l walltime=02:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q share 
#PBS -l select=1:ncpus=1
#PBS -m abe

# Author: Riley X. Brady
# Date: Sep 26, 2017
# Purpose: Given a folder containing individual simulations, this will use
# NCO's to first find the ensemble mean, and then subtract that out from
# each member to create residual files.

# INPUT 1 : Location of files
# INPUT 2 : Location for output of residuals
# INPUT 3 : Var name for naming the ensemble mean output.

# Transfer in all variables to GNU_Parallel.
source `which env_parallel.bash`

# Inputs from command line
VAR=HMXL
INPUT_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly/
OUTPUT_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/${VAR}

cd ${INPUT_DIR}

# First need to subset to 1920-2015
echo "Subsetting all files to 1920-2015..."
for n in {001,002,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,101,102,103,104,105}
do
    ncks -F -d time,1,1152 ${VAR}.${n}.192001-210012.nc ${VAR}.${n}.192001-201512.nc &
done
wait

echo "Computing ensemble mean..."
ncea *192001-201512.nc ${VAR}.ensemble_mean.1920-2015.nc
echo "Ensemble mean complete..."

mkdir -p ${OUTPUT_DIR}

# Compute residuals.
echo "Computing residuals..."
ls *192001-201512.nc | env_parallel 'echo {}; ncdiff {} ${VAR}.ensemble_mean.1920-2015.nc residual.{}'

# Clean up directory.
echo "Cleaning up directory..."
mv residual*.nc ${OUTPUT_DIR}
mv ${VAR}.ensemble_mean.1920-2015.nc /glade/scratch/rbrady/EBUS_BGC_Variability/global_mean/
rm *192001-201512.nc
