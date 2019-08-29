#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

seed=8191


python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_pitch \
    --LSTMSize 200 200 200 200 \
    --dropout 0.25 0.5 \
    --seed $seed \
    --featureNames tokens pos \
    --miniBatchSize 32 \
    --expName=$expName \
    --prosodyEmbeddings lstm \
    --prosodyLSTMSize 10
