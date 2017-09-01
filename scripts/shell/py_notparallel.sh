#!/bin/bash
#PBS -A P93300670
#PBS -N alt_co2_BenCS
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular 
#PBS -l select=1:ncpus=16
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

source /glade/u/home/$USER/pyenvs/py2-scipy/bin/activate

script=EBUS_extraction.py
VAR=FG_ALT_CO2
EBU=BenCS
OUT=/glade/p/work/rbrady/EBUS_BGC_Variability/${VAR}/${EBU}/

mkdir -p ${OUT}

for INPUT in /glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly/reduced*.nc
do
    python ${script} ${INPUT} ${VAR} ${EBU} ${OUT} 
done
wait
