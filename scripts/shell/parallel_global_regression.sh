#!/bin/bash
#PBS -A P93300670
#PBS -N SST_CalCS_global_regression
#PBS -l walltime=06:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=18
#PBS -m abe

# Author  : Riley X. Brady
# Date : Sep 22, 2017
# This is a modified form of the py_parallel.sh script. I wanted to save this
# one out since the global regression python script takes so many inputs.
# This onee is written in parallel so as to regress over multiple ensemble
# members simultaneously.

# Bring in the virtual environment python
`source activate py36`

script=global_regression_map.py
EBU=CalCS
GLOBAL_VAR=SST
GLOBAL_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/global_residuals/SST/
OUT_DIR=/glade/p/work/rbrady/EBUS_BGC_Variability/global_regressions/SST/${EBU}

for n in {0..33}
do
    python ${script} ${EBU} ${GLOBAL_VAR} ${n} ${GLOBAL_DIR} ${OUT_DIR} &
done
wait
