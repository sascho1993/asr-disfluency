#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_su \
    --LSTMSize 150 150 150\
    --dropout 0.25 0.25 \
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_su \
    --LSTMSize 150 150 150 150\
    --dropout 0.25 0.25 \
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_su \
    --LSTMSize 200 200 200\
    --dropout 0.25 0.25 \
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_su \
    --LSTMSize 200 200 200 200\
    --dropout 0.25 0.25 \
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName
