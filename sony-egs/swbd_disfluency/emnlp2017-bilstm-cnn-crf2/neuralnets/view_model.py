from __future__ import division
from __future__ import print_function


import os

import keras
from keras.optimizers import *
from keras.models import Model
from keras.layers import *
import math
import numpy as np
import sys
import gc
import time
import os
import tensorflow as tf
import logging
import random
import h5py
import json

from keraslayers.ChainCRF import ChainCRF

from keraslayers.ChainCRF import create_custom_objects

#modelPath = "models/exp_pitch_lstm_25/disfluency_pitch_ftokens,pos_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8707/disfluency_pitch_ftokens,pos_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8707_0.8212_0.8099_12.h5"
modelPath = "models/exp_pitch_only_lstm/disfluency_pitch_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32prosodyLSTM25_seed8191/disfluency_pitch_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191_0.2068_0.2169_35.h5"
#modelPath = "models/test_pretrained_pitch/disfluency_pitch_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_seed7444/disfluency_pitch_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_seed7444_0.2101_0.2175_10.h5"
model = keras.models.load_model(modelPath, custom_objects=create_custom_objects())

#for i in range(len(model.get_weights())):
#    print(i, model.get_weights()[i].shape)
print(model.get_weights())

#for lay in model.layers:
#    print(lay.name)
#    print(len(lay.get_weights()))

#print(model.inputs)
#print(model.layers)
#print(model.outputs)
#print(model.summary())

#model = Model(input=[inputs], output=[intermediate_layer])

"""
with h5py.File(modelPath, 'r') as f:
    mappings = json.loads(f.attrs['mappings'])
    params = json.loads(f.attrs['params'])
    modelName = f.attrs['modelName']
    labelKey = f.attrs['labelKey']

    bilstm = BiLSTM(params)
    bilstm.setMappings(mappings, None)
    bilstm.models = {modelName: model}
    bilstm.labelKeys = {modelName: labelKey}
    bilstm.idx2Labels = {}
    bilstm.idx2Labels[modelName] = {v: k for k, v in bilstm.mappings[labelKey].items()}

"""
