#!/bin/bash
#PBS -A P93300670
#PBS -N global_variability
#PBS -l walltime=00:10:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=6
#PBS -m abe

`source activate py36`

script=area_weighted_ebus_correlation.py

python ${script} CalCS PDO 0 0


