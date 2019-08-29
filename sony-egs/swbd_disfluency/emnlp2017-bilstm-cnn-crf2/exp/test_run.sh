#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g'`



python3 Train_Disfluencies.py \
    --optimizer adam \
    --dataset disfluency_silver \
    --LSTMSize 150 \
    --dropout 0.25 0.5 \
    --seed 8191 \
    --featureNames tokens \
    --miniBatchSize 32 \
    --expName=$expName


