#!/bin/bash
# INPUT 1 : EBU
# INPUT 2 : LAG


GLOBAL_VAR=SST
EBU=$1
LAG=$2
input_dir=/glade/p/work/${USER}/EBUS_BGC_Variability/global_regressions/${GLOBAL_VAR}/${EBU}/lag${LAG}
output_dir=${input_dir}/remapped

echo "Remapping to 1deg x 1deg for ${GLOBAL_VAR} in the ${EBU}..."
mkdir -p ${output_dir}

for file in `ls ${input_dir}`
do
    cdo remapbil,r360x180 -selname,r,m,p ${input_dir}/${file} ${output_dir}/remapped.${file}
done
