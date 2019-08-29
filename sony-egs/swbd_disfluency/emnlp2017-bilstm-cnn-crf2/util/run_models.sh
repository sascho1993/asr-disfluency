#!/bin/bash

# Run latest models of one expriment on selected test file
# Compute F-score on results and write all into results/[experiment]
# Usage:
#   sh run_models.sh models/[experiment] data/[experiment]/[train,dev,test].txt

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

# path to the parent directory of the models, e.g. models/disfluency_silver
model_path=$1
pred_file=$2
echo $model_path

if [[ "$pred_file" = *"test.txt" ]]
  then
  split="test"
elif [[ "$pred_file" = *"train.txt" ]]
  then
  split="train"
elif [[ "$pred_file" = *"dev.txt" ]]
  then
  split="dev"
fi

experiment=`echo $model_path | sed 's/models\///g'`
mkdir -p results/$experiment

for model_dir in $model_path/*
  do
    echo $model_dir
    # choose latest model
    model=`ls $model_dir | tail -1`
    model_name=`echo $model | sed 's/\.h5//g'`

    output_file=`echo $model"_"$split`
    echo "model: "$model
    echo "output file: "$output_file
    python3 RunModel_CoNLL_Format.py $model_dir/$model $pred_file > results/$experiment/$output_file
  done


for file in results/$experiment/*_$split
do
  python util/compute_normal_disfluency_fscore.py $pred_file $file
done > results/$experiment/${split}_results
