#!/bin/bash
#BSUB -P P93300670             # project code
#BSUB -W 00:30                    # wall-clock time (hrs:mins)
#BSUB -n 16                        # number of tasks in job
#BSUB -J extract-CCS                    # job name
#BSUB -o extract-CCS.%J.out             # output file name in which %J is replaced by the job ID
#BSUB -e extract-CCS.%J.err             # error file name in which %J is replaced by the job ID
#BSUB -q geyser                   # queue - must be either geyser or caldera
#BSUB -B                                                                                              $
#BSUB -N

# Author  : Riley X. Brady
# Date    : 06/01/2017
# Purpose : Use basic UNIX constructs to throughput a number of ensemble members into a
# Python script (with independent operations of course).

script=EBUS_extraction.py
VAR=FG_CO2
EBU=HumCS
OUT=/glade/p/work/rbrady/EBUS_BGC_Variability/${VAR}/${EBU}/

mkdir -p ${OUT}

time (
for INPUT in /glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly/reduced*.nc
do
    python ${script} ${INPUT} ${VAR} ${EBU} ${OUT} &
done
wait
)
