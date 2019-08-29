#!/bin/bash

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

expName=$(basename $0)
expName=`echo $expName | sed 's/\.sh//g' | sed 's/run_//g'`

filter="10 15 20 25 30 35 40 45 50 55 60 65 70 75 80"

for fil in $filter
do
    python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pitch \
        --LSTMSize 200 200 200 200 \
        --dropout 0.25 0.5 \
        --featureNames tokens pos \
        --miniBatchSize 32 \
        --expName=$expName \
        --prosodyEmbeddings cnn \
        --prosodyFilterSize $fil
done
