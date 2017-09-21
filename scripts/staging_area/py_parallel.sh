#!/bin/bash
#PBS -A P93300670
#PBS -N ALK_CanCS 
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=16
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

# Bring in the virtual environment python
`source activate py36`

# Transfer in all variables to GNU_Parallel
source `which env_parallel.bash`

script=EBUS_extraction.py
VAR=ALK
EBU=CanCS
OUT=/glade/p/work/rbrady/EBUS_BGC_Variability/${VAR}/${EBU}/

mkdir -p ${OUT}

ls /glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly/reduced*.nc | env_parallel 'echo {}; python ${script} {} ${VAR} ${EBU} ${OUT}'

# for INPUT in /glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly/reduced*.nc
# do
#     python ${script} ${INPUT} ${VAR} ${EBU} ${OUT} &
# done
# wait
