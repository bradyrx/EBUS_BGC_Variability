#!/bin/bash
#PBS -A P93300670
#PBS -N global_variability
#PBS -l walltime=01:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=18
#PBS -m abe

`source activate py36`

script=global_seasonal_internal_magnitudes.py
VAR=FG_ALT_CO2

python ${script} ${VAR}
