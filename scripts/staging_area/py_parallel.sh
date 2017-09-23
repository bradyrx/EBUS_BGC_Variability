#!/bin/bash
#PBS -A P93300670
#PBS -N SST_CalCS_global_regression
#PBS -l walltime=10:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=8
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

# Bring in the virtual environment python
`source activate py36`

script=global_regression_map.py
EBU=CalCS
GLOBAL_VAR=SST
GLOBAL_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/SST/
OUT_DIR=/glade/p/work/rbrady/EBUS_BGC_Variability/global_regressions/SST/${EBU}

for n in {0..33}
do
    python ${script} ${EBU} ${GLOBAL_VAR} ${n} ${GLOBAL_DIR} ${OUT_DIR} 
done
