#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

seed=8191
lstm_size="10 15 25 50 75"

for lstm in $lstm_size
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pitch \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --featureNames tokens pos \
        --miniBatchSize 32 \
        --seed $seed \
        --expName=$expName \
        --prosodyEmbeddings lstm \
        --prosodyLSTMSize $lstm
done
