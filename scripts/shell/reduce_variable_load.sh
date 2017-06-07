#!/bin/bash
#BSUB -P P93300670             # project code
#BSUB -W 00:30                    # wall-clock time (hrs:mins)
#BSUB -n 16                       # number of tasks in job
#BSUB -J FG_CO2-reduce                    # job name
#BSUB -o FG_CO2-reduce.%J.out             # output file name in which %J is replaced by the job ID
#BSUB -e FG_CO2-reduce.%J.err             # error file name in which %J is replaced by the job ID
#BSUB -q geyser                   # queue - must be either geyser or caldera
#BSUB -B                                                                                              $
#BSUB -N

# Author  : Riley X. Brady
# Date    : 05/25/2017
# Purpose : Quick script to take output from CESM-LENS that has MANY variables embedded, and just pull out the variable and coordinates of interest. 
# This makes it easier to manage when loading a bunch of files into xArray.

MAIN_DIR=/glade/scratch/rbrady/fgco2_monthly
VAR=FG_CO2
LAT=TLAT
LON=TLONG
AREA=TAREA

cd ${MAIN_DIR}

ls *.nc | parallel 'echo {}; ncks -v FG_CO2,TLAT,TLONG,TAREA {} reduced.{}'
