#!/bin/bash
#PBS -A P93300670
#PBS -N CalCS_PDO
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular 
#PBS -l select=1:ncpus=1
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).
source activate py36

script=overhead_spatial_correlation.py
EBU=CalCS
VARX=PDO
LAG=0
SMOOTH=0

for ENS in {0..33}
do
    python ${script} ${EBU} ${VARX} ${ENS} ${LAG} ${SMOOTH}
done
wait
