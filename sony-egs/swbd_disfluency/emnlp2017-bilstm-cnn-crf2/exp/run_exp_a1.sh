#!/bin/bash

# To be set:
	# dataset
	# LSTM-Size
	# dropout
	# seed
	# FeatureNames

. env/bin/activate
. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

exp=$(basename $0)
expName=`echo $exp | sed 's/\.sh//g' | sed 's/run_//g'`	

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 100 \
    --dropout 0 \
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 100 100 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 100 100 100 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName
    
python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 150 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 150 150 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 150 150 150 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName
    
python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 200 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 200 200 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 200 200 200 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 250 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 250 250 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName

python3 Train_Disfluencies.py \
    --optimizer nadam \
    --dataset disfluency_su \
    --LSTMSize 250 250 250 \
    --dropout 0\
    --seed 8191 \
    --featureNames tokens \
    --expName=$expName
