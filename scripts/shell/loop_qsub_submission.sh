#!/bin/bash


for N in {0..2}
do
    qsub -v ensemble=${N},lag=6 single_ens_regression.sh 
    sleep 1 
done
