#!/bin/bash

# same as run_models.sh but for all test files in kaldi_test
# results are written to results/kaldi_test/[experiment]

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

# path to the parent directory of the models, e.g. models/disfluency_su_ftokens
model_path=$1
partition=$2
echo $model_path


experiment=`echo $model_path | sed 's/models\///g'`
#mkdir -p results/kaldi_test/$experiment

#for pred_file in data/kaldi_test/${partition}_{5,6,7,8,9,10,11}*.txt
#for pred_file in data/kaldi_test/${partition}_{12,13,14,15,16,17}*.txt
for pred_file in data/kaldi_test/${partition}_*.txt
do
  split=`echo $pred_file | sed 's/\.txt//g' | sed 's/data\/kaldi_test\/test_//g' | sed 's/data\/kaldi_test\/dev_//g'`
  #mkdir results/kaldi_test/$experiment/$split
  for model_dir in $model_path/*
    do
      echo $model_dir
      # choose latest model
      model=`ls $model_dir | tail -1`
      model_name=`echo $model | sed 's/\.h5//g'`

      output_file=`echo $model"_"$partition"_"$split`
      echo "model: "$model
      echo "output file: "$output_file
      #python3 RunModel_CoNLL_Format.py $model_dir/$model $pred_file > results/kaldi_test/$experiment/$split/$output_file
    done
  for file in results/kaldi_test/$experiment/$split/*${partition}_$split
  do
    python util/compute_normal_disfluency_fscore.py $pred_file $file
  done > results/kaldi_test/$experiment/$split/${partition}_${split}_results
done
