#!/bin/bash
# Loops through to submit lags 0 through 6 months and 3 simulations as a test
# case.

for LAG in {0..6}
do
for N in {0..2}
do
    qsub -v ensemble=${N},L=${LAG} single_ens_regression.sh 
    sleep 0.5 
done
done
