#!/bin/bash
#PBS -A P93300670
#PBS -N landschuetzer_global 
#PBS -l walltime=01:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q regular
#PBS -l select=1:ncpus=18
#PBS -m abe

`source activate py36`

script=create_POP_landschuetzer_residuals.py
out=/glade/p/work/rbrady/EBUS_BGC_Variability

python ${script} ${out}


