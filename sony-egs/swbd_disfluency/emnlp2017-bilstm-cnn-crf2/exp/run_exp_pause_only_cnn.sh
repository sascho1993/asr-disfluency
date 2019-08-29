#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

seeds="7687 8191 8423 8707 8933"

for seed in $seeds
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pause \
        --LSTMSize 200 200 200 200 \
        --seed $seed \
        --dropout 0.25 0.5 \
        --miniBatchSize 32 \
        --expName=$expName \
        --featureNames pause \
        --prosodyEmbeddings None
done
