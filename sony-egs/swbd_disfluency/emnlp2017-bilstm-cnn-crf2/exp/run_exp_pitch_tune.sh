#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

p_filter_sizes="10 30 50 100"
seed=8191

for filter_size in $p_filter_sizes
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pitch \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --seed $seed \
        --featureNames tokens pos \
        --miniBatchSize 32 \
        --expName=$expName \
        --prosodyEmbeddings cnn \
        --prosodyFilterSize=$filter_size
done
