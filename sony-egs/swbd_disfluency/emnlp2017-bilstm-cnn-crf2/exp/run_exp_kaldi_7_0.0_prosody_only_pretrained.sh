#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

#seeds="6257 6571 7013 7039 7333 7577 7687 8191 8423 8707 8933 9661 9739 9907 9973"
#seeds="6257 6571 7013 7039 7333 7577 7687 8191"
seeds="8423 8707 8933 9661 9739 9907 9973"

for seed in $seeds
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset 7_0.0 \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --seed $seed \
        --featureNames pause word_dur_word \
        --miniBatchSize 32 \
        --expName=$expName \
        --prosodyEmbeddings pretrained
done

