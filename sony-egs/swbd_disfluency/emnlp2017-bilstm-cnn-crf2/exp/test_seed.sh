#!/bin/bash

# To be set:
	# dataset
	# LSTM-Size
	# dropout
	# seed
	# FeatureNames

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

exp=$(basename $0)
expName=`echo $exp | sed 's/\.sh//g' | sed 's/run_//g'`	

python3 Train_Disfluencies.py \
        --optimizer adam \
        --dataset disfluency_pitch \
        --LSTMSize 100 \
        --dropout 0.25 0.5 \
        --seed 8191 \
        --featureNames tokens pos \
        --miniBatchSize 64 \
        --expName=$expName \
        --prosodyEmbeddings cnn \
        --prosodyFilterSize=10

