#!/bin/bash
#PBS -A P93300670
#PBS -N U10_BenCS_gregress_unsmoothed
#PBS -l walltime=00:30:00
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
VARY=NPGO
GLOBAL_VAR=SST
smoothing=False

python ${script} ${VARY} ${GLOBAL_VAR} ${L} ${ensemble} ${smoothing}  
