#!/bin/bash
#PBS -A P93300670
#PBS -N global_residual_SST
#PBS -l walltime=10:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy 
#PBS -l select=1:ncpus=8
#PBS -m abe

`source activate py36`

script=create_global_residuals.py
VAR=SST
DIR=/glade/p/work/rbrady/EBUS_BGC_Variability/${VAR}/global/

python ${script} ${VAR} ${DIR}


