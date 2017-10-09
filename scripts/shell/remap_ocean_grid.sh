#!/bin/bash
# This script loops through a folder of native ocean grid output and remaps it
# to a 180x360 standard grid. This helps for plotting contours, and for things
# like curl calculation.
#PBS -A P93300670
#PBS -N remap_TAUX
#PBS -l walltime=01:30:00
#PBS -M riley.brady@colorado.edu
#PBS -q economy
#PBS -l select=1:ncpus=6
#PBS -m abe
VAR=TAUX

# Load appropriate CDO version
source /glade/u/apps/opt/lmod/4.2.1/init/bash
module load cdo 

INPUT_DIR=/glade/scratch/rbrady/EBUS_BGC_Variability/${VAR}_monthly
mkdir -p ${INPUT_DIR}/remapped/

for n in {001,002,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,101,102,103,104,105}
do
    echo "Remapping ${n}..."
    cdo remapbil,r360x180 -selname,${VAR} ${INPUT_DIR}/${VAR}.${n}.192001-210012.nc ${INPUT_DIR}/remapped/remapped.${VAR}.${n}.192001-210012.nc
done
