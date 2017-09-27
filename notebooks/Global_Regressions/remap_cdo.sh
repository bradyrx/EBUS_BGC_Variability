#!/bin/bash
# INPUT 1 : VAR 
# INPUT 2 : EBU 
# INPUT 3 : LAG

GLOBAL_VAR=$1
EBU=$2
LAG=$3
input_dir=/glade/p/work/${USER}/EBUS_BGC_Variability/global_regressions/${GLOBAL_VAR}/${EBU}/lag${LAG}

current_dir=`pwd`

echo "Remapping to 1deg x 1deg for ${GLOBAL_VAR} in the ${EBU}..."
cd ${input_dir}
for file in `ls ${GLOBAL_VAR}*.nc`
do
    cdo remapbil,r360x180 -selname,r,m,p ${file} remapped.${file}
done
rm ${GLOBAL_VAR}*.nc
cd ${current_dir}
