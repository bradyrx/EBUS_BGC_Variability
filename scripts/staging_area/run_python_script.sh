#!/bin/bash
#PBS -A P93300670
#PBS -N TAUY2_BenCS 
#PBS -l walltime=01:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=8
#PBS -m abe

source /glade/u/home/rbrady/anaconda3/bin/activate

script=generate_regional_residuals.py
EBU=BenCS
VAR=TAUY2

python ${script} ${EBU} ${VAR}


