#!/bin/bash
#PBS -A P93300670
#PBS -N bencs 
#PBS -l walltime=00:20:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=1
#PBS -m abe

`source activate py36`

script=generate_regional_residuals.py
EBUS=BenCS
VAR=Jint_100m_DIC

python ${script} ${EBUS} ${VAR}


