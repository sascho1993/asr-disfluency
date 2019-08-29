from __future__ import print_function
#from util import BIOF1Validation

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0";

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
import random
import logging

from keraslayers.ChainCRF import ChainCRF

def setMappings(self, mappings, embeddings):
    self.embeddings = embeddings
    self.mappings = mappings

def loadModel(modelPath):
    import h5py
    import json
    from keraslayers.ChainCRF import create_custom_objects

    model = keras.models.load_model(modelPath, custom_objects=create_custom_objects())

    with h5py.File(modelPath, 'r') as f:
        mappings = json.loads(f.attrs['mappings'])
        params = json.loads(f.attrs['params'])
        modelName = f.attrs['modelName']
        labelKey = f.attrs['labelKey']
    for key in mappings:
        print (key.encode('utf-8'))
"""
    bilstm = BiLSTM(params)
    bilstm.setMappings(mappings, None)
    bilstm.models = {modelName: model}
    bilstm.labelKeys = {modelName: labelKey}
    bilstm.idx2Labels = {}
    bilstm.idx2Labels[modelName] = {v: k for k, v in bilstm.mappings[labelKey].items()}"""
    #return bilstm

loadModel("../models/unidep_pos_0.9300_0.9318_1.h5")
