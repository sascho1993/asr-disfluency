#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

seeds="6257 6571 7013 7039 7333 7577 8191 8423 8707 8933 9661 9739 9907 9973"
#seeds="6257 6571 7013 7039 7333 7577 7687 8191 8423 8707 8933 9661 9739 9907 9973"
#seeds="7687"

for seed in $seeds
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_duration \
        --LSTMSize 200 200 200 200 \
        --seed $seed \
        --dropout 0.25 0.5 \
        --miniBatchSize 32 \
        --expName=$expName \
        --featureNames word_dur_phone \
        --prosodyEmbeddings None
done

