#!/bin/bash
LAG=0

for N in {0..2}
do
    qsub -v ensemble=${N},L=${LAG} single_ens_regression.sh 
    sleep 1 
done
