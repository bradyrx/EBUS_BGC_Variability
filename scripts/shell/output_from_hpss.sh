#!/bin/bash
# Used to retrieve files from tape.
#PBS -A P93300670
#PBS -N pull_from_tape 
#PBS -l walltime=024:00:00
#PBS -M riley.brady@colorado.edu
#PBS -q hpss 
#PBS -l select=1:ncpus=1
#PBS -m abe

COMP=ocn # Replace with model component you are drawing from
RES=monthly # Replace with resolution you are drawing from
VAR=ATM_ALT_CO2 # Replace with variable you are pulling from tape

# Leave everything below as is

cd "/glade/scratch/${USER}"
mkdir -p "CESM-CAM5-BGC-LE/${COMP}/proc/tseries/${RES}/${VAR}"
cd "CESM-CAM5-BGC-LE/${COMP}/proc/tseries/${RES}/${VAR}"

hsi "cd /CCSM/csm/CESM-CAM5-BGC-LE/${COMP}/proc/tseries/${RES}/${VAR} ; mget * ; bye"
exit 0

