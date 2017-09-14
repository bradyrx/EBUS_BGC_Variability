#!/bin/bash
#PBS -A P93300670
#PBS -N alt_co2_CalCS
#PBS -l walltime=00:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular 
#PBS -l select=1:ncpus=16
#PBS -m abe

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

script=create_fg_ant_co2.py
EBU=BenCS

mkdir -p ${OUT}

for n in {001,002,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,101,102,103,104,105}
do
    python ${script} ${n} ${EBU} 
done
wait
