#!/bin/bash
#BSUB -P P93300670             # project code
#BSUB -W 00:45                   # wall-clock time (hrs:mins)
#BSUB -n 1                       # number of tasks in job
#BSUB -J run_py                    # job name
#BSUB -o run_py.%J.out             # output file name in which %J is replaced by the job ID
#BSUB -e run_py.%J.err             # error file name in which %J is replaced by the job ID
#BSUB -q geyser                   # queue - must be either geyser or caldera
#BSUB -B                                                                                              $
#BSUB -N

# Author  : Riley X. Brady
# Date    : 07/10/2017
# Purpose : Use this when submitting a python script as a job.
script=overhead-pco2-taylor-slopes-and-sensitivities.py
EBU=BenCS
VAR=sam

python ${script} ${EBU} ${VAR}


