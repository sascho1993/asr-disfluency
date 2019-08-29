#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

seed=8191
lstm_sizes="10 25 50 75"

for size in $lstm_sizes
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pitch \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --miniBatchSize 32 \
        --seed $seed \
        --expName=$expName \
        --prosodyEmbeddings lstm \
        --prosodyLSTMSize $size
done
