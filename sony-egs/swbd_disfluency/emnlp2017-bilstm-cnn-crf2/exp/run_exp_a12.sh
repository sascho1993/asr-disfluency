#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 150 150 150 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 256 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 150 150 150 150 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 256 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 200 200 200 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 256 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 200 200 200 200 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 256 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 150 150 150 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 512 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 150 150 150 150 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 512 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 200 200 200 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 512 \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency \
    --LSTMSize 200 200 200 200 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 512 \
    --expName=$expName
