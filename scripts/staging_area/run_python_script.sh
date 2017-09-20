#!/bin/bash
#PBS -A P93300670
#PBS -N global_variability
#PBS -l walltime=01:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=6
#PBS -m abe

module unload python

script=global_seasonal_internal_magnitudes.py
VAR=FG_ALT_CO2

~/anaconda3/bin/python3.6 ${script} ${VAR}


