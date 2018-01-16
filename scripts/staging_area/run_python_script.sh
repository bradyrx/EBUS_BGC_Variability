#!/bin/bash
#PBS -A P93300670
#PBS -N SSH_NPGO 
#PBS -l walltime=01:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=1
#PBS -m abe

`source activate py36`

script=global_regression_map.py
varx=NPGO
vary=SLP
LAG=0
ENS=1
SMOOTH=False

python ${script} ${varx} ${vary} ${LAG} ${ENS} ${SMOOTH} 


