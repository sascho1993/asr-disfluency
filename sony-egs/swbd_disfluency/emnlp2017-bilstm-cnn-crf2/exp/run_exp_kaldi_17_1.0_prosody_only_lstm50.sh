#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

#seeds="8191"
seeds="7333"

for seed in $seeds
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset 17_1.0 \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --seed $seed \
        --miniBatchSize 32 \
        --expName=$expName \
        --prosodyEmbeddings lstm \
        --prosodyLSTMSize 50
done
