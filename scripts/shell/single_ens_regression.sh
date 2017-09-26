#!/bin/bash
#PBS -A P93300670
#PBS -N SST_HumCS_gregress
#PBS -l walltime=00:45:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy 
#PBS -l select=1:ncpus=1
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

# Bring in the virtual environment python
`source activate py36`

script=global_regression_map.py
EBU=HumCS
GLOBAL_VAR=SST
GLOBAL_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/SST/
OUT_DIR=/glade/p/work/rbrady/EBUS_BGC_Variability/global_regressions/SST/${EBU}/lag${LAG}/

python ${script} ${EBU} ${GLOBAL_VAR} ${lag} ${ensemble} ${GLOBAL_DIR} ${OUT_DIR} 
