"""
A bidirectional LSTM with optional CRF and character-based presentation for NLP sequence tagging used for multi-task learning.

Author: Nils Reimers
License: Apache-2.0
"""
from __future__ import division
from __future__ import print_function


from util import BIOF1Validation

import os 
#os.environ["CUDA_VISIBLE_DEVICES"] = "0";

import keras
from keras.optimizers import *
from keras.models import Model
from keras.layers import *
from keras.utils import multi_gpu_model
import math
import numpy as np
import sys
import gc
import time
import os
import tensorflow as tf
import logging
import random

from .keraslayers.ChainCRF import ChainCRF


#from numpy.random import seed
#seed(8191)
#from tensorflow import set_random_seed
#set_random_seed(8191)
#import random
#random.seed(8191)


class BiLSTM:
    def __init__(self, params=None):
        # modelSavePath = Path for storing models, resultsSavePath = Path for storing output labels while training
        self.models = None
        self.modelSavePath = None
        self.resultsSavePath = None

        # Hyperparameters for the network
        defaultParams = {'dropout': (0.5,0.5), 'classifier': ['Softmax'], 'LSTM-Size': (100,), 'customClassifier': {},
                         'optimizer': 'adam',
                         'charEmbeddings': None, 'charEmbeddingsSize': 30, 'charFilterSize': 30, 'charFilterLength': 3, 'charLSTMSize': 25, 'maxCharLength': 25,
                         'prosodyEmbeddings': None, 'numberProsodyFeatures' : 3, 'prosodyFilterSize': 30, 'prosodyFilterLength': [3,4,5], 'prosodyLSTMSize': 25, 'maxProsodyLength': 422, 'pretrainedWeights' : None,
                         'useTaskIdentifier': False, 'clipvalue': 0, 'clipnorm': 1,
                         'earlyStopping': 5, 'miniBatchSize': 32,
                         'featureNames': ['tokens', 'casing'], 'addFeatureDimensions': 10,
                         'seed' : None }

        if params != None:
            defaultParams.update(params)
        self.params = defaultParams

        if self.params['seed'] != None:
          np.random.seed(self.params['seed'])
          tf.set_random_seed(self.params['seed'])
          random.seed(self.params['seed'])




    def setMappings(self, mappings, embeddings):
        self.embeddings = embeddings
        self.mappings = mappings

    def setDataset(self, datasets, data):
        self.datasets = datasets
        self.data = data

        # Create some helping variables
        self.mainModelName = None
        self.epoch = 0
        self.learning_rate_updates = {'sgd': {1: 0.1, 3: 0.05, 5: 0.01}}
        #self.learning_rate_updates = {'adam': {1: 0.001, 5: 0.0005, 10: 0.0001, 15: 0.00005}}
        self.modelNames = list(self.datasets.keys())
        self.evaluateModelNames = []
        self.labelKeys = {}
        self.idx2Labels = {}
        self.trainMiniBatchRanges = None
        self.trainSentenceLengthRanges = None
        self.devMiniBatchRanges = None
        self.devSentenceLengthRanges = None
        


        for modelName in self.modelNames:
            labelKey = self.datasets[modelName]['label']
            self.labelKeys[modelName] = labelKey
            self.idx2Labels[modelName] = {v: k for k, v in self.mappings[labelKey].items()}
            
            if self.datasets[modelName]['evaluate']:
                self.evaluateModelNames.append(modelName)
            
            logging.info("--- %s ---" % modelName)
            logging.info("%d train sentences" % len(self.data[modelName]['trainMatrix']))
            logging.info("%d dev sentences" % len(self.data[modelName]['devMatrix']))
            logging.info("%d test sentences" % len(self.data[modelName]['testMatrix']))
            
        
        if len(self.evaluateModelNames) == 1:
            self.mainModelName = self.evaluateModelNames[0]
             
        self.casing2Idx = self.mappings['casing']

        if self.params['charEmbeddings'] not in [None, "None", "none", False, "False", "false"]:
            logging.info("Pad words to uniform length for characters embeddings")
            all_sentences = []
            for dataset in self.data.values():
                for data in [dataset['trainMatrix'], dataset['devMatrix'], dataset['testMatrix']]:
                    for sentence in data:
                        all_sentences.append(sentence)
            self.padCharacters(all_sentences)
            logging.info("Words padded to %d characters" % (self.maxCharLen))

        
    def buildModel(self):
        self.models = {}

        if 'tokens' in self.params['featureNames']:
            tokens_input = Input(shape=(None,), dtype='int32', name='words_input')
            tokens = Embedding(input_dim=self.embeddings.shape[0], output_dim=self.embeddings.shape[1], weights=[self.embeddings], trainable=False, name='word_embeddings')(tokens_input)

            inputNodes = [tokens_input]
            mergeInputLayers = [tokens]
        else:
            inputNodes = []
            mergeInputLayers = []
        for featureName in self.params['featureNames']:
            if featureName == 'tokens' or featureName == 'characters' or featureName == 'prosody':
                continue
            if featureName == 'pause' or featureName == 'word_dur_phone' or featureName == 'word_dur_word' or featureName == 'pause_before' or featureName == 'pause_after':
                #def log_activation(x):
                #    return keras.backend.minimum(1.0, keras.backend.log((x/100)+1))
                feature_input = Input(shape=(None,), dtype='float32', name=featureName+'_input')
                #feature_val = Activation(log_activation)(feature_input)
                feature_val = Activation('linear')(feature_input)
                feature_val = Reshape((-1, 1))(feature_val)
                
                inputNodes.append(feature_input)
                mergeInputLayers.append(feature_val)
                continue
            # embeddings for all other features are trained, e.g. pos
            feature_input = Input(shape=(None,), dtype='int32', name=featureName+'_input')
            feature_embedding = Embedding(input_dim=len(self.mappings[featureName]), output_dim=self.params['addFeatureDimensions'], name=featureName+'_embeddings')(feature_input)

            inputNodes.append(feature_input)
            mergeInputLayers.append(feature_embedding)
        

        # :: Character Embeddings ::
        if self.params['charEmbeddings'] not in [None, "None", "none", False, "False", "false"]:
            charset = self.mappings['characters']
            charEmbeddingsSize = self.params['charEmbeddingsSize']
            maxCharLen = self.maxCharLen
            charEmbeddings = []
            for _ in charset:
                limit = math.sqrt(3.0 / charEmbeddingsSize)
                vector = np.random.uniform(-limit, limit, charEmbeddingsSize)
                charEmbeddings.append(vector)

            charEmbeddings[0] = np.zeros(charEmbeddingsSize)  # Zero padding
            charEmbeddings = np.asarray(charEmbeddings)

            chars_input = Input(shape=(None, maxCharLen), dtype='int32', name='char_input')
            #print('chars_input', chars_input.shape)
            mask_zero = (self.params['charEmbeddings'].lower()=='lstm') #Zero mask only works with LSTM
            chars = TimeDistributed(
                Embedding(input_dim=charEmbeddings.shape[0], output_dim=charEmbeddings.shape[1],
                          weights=[charEmbeddings],
                          trainable=True, mask_zero=mask_zero), name='char_emd')(chars_input)

            if self.params['charEmbeddings'].lower()=='lstm':  # Use LSTM for char embeddings from Lample et al., 2016
                charLSTMSize = self.params['charLSTMSize']
                chars = TimeDistributed(Bidirectional(LSTM(charLSTMSize, return_sequences=False)), name="char_lstm")(
                    chars)
            else:  # Use CNNs for character embeddings from Ma and Hovy, 2016
                charFilterSize = self.params['charFilterSize']
                charFilterLength = self.params['charFilterLength']
                chars = TimeDistributed(Conv1D(charFilterSize, charFilterLength, padding='same'), name="char_cnn")(
                    chars)
                chars = TimeDistributed(GlobalMaxPooling1D(), name="char_pooling")(chars)

            self.params['featureNames'].append('characters')
            mergeInputLayers.append(chars)
            inputNodes.append(chars_input)
            
        # :: Prosody Embeddings ::
        if self.params['prosodyEmbeddings'] not in [None, "None", "none", False, "False", "false"]:
            if self.params['prosodyEmbeddings'].lower()=='cnn':
                maxProsodyLen = self.params['maxProsodyLength']
                numberProsodyFeatures = self.params['numberProsodyFeatures']
                prosody_input = Input(shape=(None, maxProsodyLen, numberProsodyFeatures), dtype='float32', name='prosody_input')
                prosodyFilterSize = int(self.params['prosodyFilterSize'])
                prosodyFilterLength = self.params['prosodyFilterLength']
                for i in prosodyFilterLength:
                    prosody = TimeDistributed(Conv1D(prosodyFilterSize, i, padding='same'), name="prosody_cnn_{}".format(i))(prosody_input)
                    prosody = TimeDistributed(GlobalMaxPooling1D(), name="prosody_pooling_{}".format(i))(prosody)
                    mergeInputLayers.append(prosody)
                self.params['featureNames'].append('prosody')
                inputNodes.append(prosody_input)
            elif self.params['prosodyEmbeddings'].lower()=='lstm':
                maxProsodyLen = self.params['maxProsodyLength']
                numberProsodyFeatures = self.params['numberProsodyFeatures']
                prosody_input = Input(shape=(None, maxProsodyLen, numberProsodyFeatures), dtype='float32', name='prosody_input')
                prosodyLSTMSize = self.params['prosodyLSTMSize']
                prosody = TimeDistributed(Bidirectional(LSTM(prosodyLSTMSize, return_sequences=False)), name="prosody_lstm")(
                    prosody_input)
                self.params['featureNames'].append('prosody')
                mergeInputLayers.append(prosody)
                inputNodes.append(prosody_input)
            elif self.params['prosodyEmbeddings'].lower()=='pretrained':
                from .keraslayers.ChainCRF import create_custom_objects
                maxProsodyLen = self.params['maxProsodyLength']
                # use 25 units for one prosodic feature and 50 units for all three prosodic features together
                #prosodyLSTMSize = self.params['prosodyLSTMSize']
                if self.params['pretrainedWeights'] == "pitch" or self.params['pretrainedWeights'] == "energy" or self.params['pretrainedWeights'] == "formants":
                    prosodyLSTMSize = 25
                elif self.params['pretrainedWeights'] == "pitch_energy_formants" or self.params['pretrainedWeights'] == "kaldi_prosody_7_0.0" or self.params['pretrainedWeights'] == "kaldi_prosody_17_1.0":
                    prosodyLSTMSize = 50
                numberProsodyFeatures = self.params['numberProsodyFeatures']
                prosody_input = Input(shape=(None, maxProsodyLen, numberProsodyFeatures), dtype='float32', name='prosody_input')
                prosody = TimeDistributed(Bidirectional(LSTM(prosodyLSTMSize, return_sequences=False)), name="prosody_lstm")(
                    prosody_input)
                self.params['featureNames'].append('prosody')
                mergeInputLayers.append(prosody)
                inputNodes.append(prosody_input)
        # :: Task Identifier :: 
        if self.params['useTaskIdentifier']:
            self.addTaskIdentifier()
            
            taskID_input = Input(shape=(None,), dtype='int32', name='task_id_input')
            taskIDMatrix = np.identity(len(self.modelNames), dtype='float32')
            taskID_outputlayer = Embedding(input_dim=taskIDMatrix.shape[0], output_dim=taskIDMatrix.shape[1], weights=[taskIDMatrix], trainable=False, name='task_id_embedding')(taskID_input)
        
            mergeInputLayers.append(taskID_outputlayer)
            inputNodes.append(taskID_input)
            self.params['featureNames'].append('taskID')

        if len(mergeInputLayers) >= 2:
            merged_input = concatenate(mergeInputLayers)
        else:
            merged_input = mergeInputLayers[0]
        
        
        # Add LSTMs
        shared_layer = merged_input
        logging.info("LSTM-Size: %s" % str(self.params['LSTM-Size']))
        cnt = 1
        for size in self.params['LSTM-Size']:      
            if isinstance(self.params['dropout'], (list, tuple)): 
                shared_layer = Bidirectional(LSTM(size, return_sequences=True, dropout=self.params['dropout'][0], recurrent_dropout=self.params['dropout'][1]), name='shared_varLSTM_'+str(cnt))(shared_layer)
            else:
                """ Naive dropout """
                shared_layer = Bidirectional(LSTM(size, return_sequences=True), name='shared_LSTM_'+str(cnt))(shared_layer) 
                if self.params['dropout'] > 0.0:
                    shared_layer = TimeDistributed(Dropout(self.params['dropout']), name='shared_dropout_'+str(self.params['dropout'])+"_"+str(cnt))(shared_layer)
            
            cnt += 1
            
            
        for modelName in self.modelNames:
            output = shared_layer
            
            modelClassifier = self.params['customClassifier'][modelName] if modelName in self.params['customClassifier'] else self.params['classifier']

            if not isinstance(modelClassifier, (tuple, list)):
                modelClassifier = [modelClassifier]
            
            cnt = 1
            for classifier in modelClassifier:
                n_class_labels = len(self.mappings[self.labelKeys[modelName]])

                if classifier == 'Softmax':
                    output = TimeDistributed(Dense(n_class_labels, activation='softmax'), name=modelName+'_softmax')(output)
                    lossFct = 'sparse_categorical_crossentropy'
                elif classifier == 'CRF':
                    output = TimeDistributed(Dense(n_class_labels, activation=None),
                                             name=modelName + '_hidden_lin_layer')(output)
                    crf = ChainCRF(name=modelName+'_crf')
                    output = crf(output)
                    lossFct = crf.sparse_loss
                elif isinstance(classifier, (list, tuple)) and classifier[0] == 'LSTM':
                            
                    size = classifier[1]
                    if isinstance(self.params['dropout'], (list, tuple)): 
                        output = Bidirectional(LSTM(size, return_sequences=True, dropout=self.params['dropout'][0], recurrent_dropout=self.params['dropout'][1]), name=modelName+'_varLSTM_'+str(cnt))(output)
                    else:
                        """ Naive dropout """ 
                        output = Bidirectional(LSTM(size, return_sequences=True), name=modelName+'_LSTM_'+str(cnt))(output) 
                        if self.params['dropout'] > 0.0:
                            output = TimeDistributed(Dropout(self.params['dropout']), name=modelName+'_dropout_'+str(self.params['dropout'])+"_"+str(cnt))(output)                    
                else:
                    assert(False) #Wrong classifier
                    
                cnt += 1
                
            # :: Parameters for the optimizer ::
            optimizerParams = {}
            if 'clipnorm' in self.params and self.params['clipnorm'] != None and  self.params['clipnorm'] > 0:
                optimizerParams['clipnorm'] = self.params['clipnorm']
            
            if 'clipvalue' in self.params and self.params['clipvalue'] != None and  self.params['clipvalue'] > 0:
                optimizerParams['clipvalue'] = self.params['clipvalue']
            
            if self.params['optimizer'].lower() == 'adam':
                opt = Adam(**optimizerParams)
            elif self.params['optimizer'].lower() == 'nadam':
                opt = Nadam(**optimizerParams)
            elif self.params['optimizer'].lower() == 'rmsprop': 
                opt = RMSprop(**optimizerParams)
            elif self.params['optimizer'].lower() == 'adadelta':
                opt = Adadelta(**optimizerParams)
            elif self.params['optimizer'].lower() == 'adagrad':
                opt = Adagrad(**optimizerParams)
            elif self.params['optimizer'].lower() == 'sgd':
                opt = SGD(lr=0.1, **optimizerParams)
            
            
            model = Model(inputs=inputNodes, outputs=[output])
            # Use pretrained prosody embeddings
            if self.params['prosodyEmbeddings'].lower()=='pretrained':
                model.get_layer('prosody_lstm').trainable = False
                if self.params['pretrainedWeights'] == "pitch":
                    prosodyModelPath = "models/exp_pitch_only_lstm/disfluency_pitch_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32prosodyLSTM25_seed8191/disfluency_pitch_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191_0.2068_0.2169_35.h5"
                elif self.params['pretrainedWeights'] == "energy":
                    prosodyModelPath = "models/exp_energy_only_lstm/disfluency_energy_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191/disfluency_energy_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191_0.1707_0.1668_24.h5"
                elif self.params['pretrainedWeights'] == "formants":
                    prosodyModelPath = "models/exp_formants_only_lstm/disfluency_formants_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191/disfluency_formants_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM25_seed8191_0.1581_0.1651_15.h5"
                elif self.params['pretrainedWeights'] == "pitch_energy_formants":
                    prosodyModelPath = "models/exp_pitch_energy_formants_only_lstm50/disfluency_prosody_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM50_seed8191/disfluency_prosody_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM50_seed8191_0.4292_0.4295_44.h5"
                elif self.params['pretrainedWeights'] == "kaldi_prosody_7_0.0":
                    prosodyModelPath = "models/exp_kaldi_7_0.0_prosody_only_lstm50/7_0.0_fNone_oadam_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM50_seed8191/7_0.0_fNone_lstm200,200,200,200_dropout0.25,0.5_mb32_prosodyLSTM50_seed8191_0.2863_0.3035_43.h5"
                else:
                    print("No pretrained weights available for this dataset")
                prosodyModel = keras.models.load_model(prosodyModelPath, custom_objects=create_custom_objects())
                prosodyWeights = prosodyModel.get_weights()[0:6]
                model.get_layer('prosody_lstm').set_weights(prosodyWeights)
            
            # Parallelise over 4 GPUs
            #parallel_model = multi_gpu_model(model, gpus=4)
            #parallel_model.compile(loss=lossFct, optimizer=opt)
            #parallel_model.summary(line_length=125)
            
            #self.models[modelName] = parallel_model
            
            #Use 1 GPU
            model.compile(loss=lossFct, optimizer=opt)
            model.summary(line_length=125)
            self.models[modelName] = model
            
            #logging.info(model.get_config())
            #logging.info("Optimizer: %s - %s" % (str(type(model.optimizer)), str(model.optimizer.get_config())))


    def trainModel(self):
        self.epoch += 1
        
        if self.params['optimizer'] in self.learning_rate_updates and self.epoch in self.learning_rate_updates[self.params['optimizer']]:       
            logging.info("Update Learning Rate to %f" % (self.learning_rate_updates[self.params['optimizer']][self.epoch]))
            for modelName in self.modelNames:            
                K.set_value(self.models[modelName].optimizer.lr, self.learning_rate_updates[self.params['optimizer']][self.epoch]) 
                
        c = 0
        train_loss = 0
        for batch in self.minibatch_iterate_dataset():
            c += 1
            for modelName in self.modelNames:         
                nnLabels = batch[modelName][0]
                nnInput = batch[modelName][1:]
                train_loss += self.models[modelName].train_on_batch(nnInput, nnLabels)
                
        train_loss = train_loss/c
        logging.info("train loss: {}".format(train_loss))
        
        c = 0
        dev_loss = 0
        for batch in self.minibatch_iterate_devset():
            c += 1
            for modelName in self.modelNames:
                nnLabels = batch[modelName][0]
                nnInput = batch[modelName][1:]
                dev_loss += self.models[modelName].test_on_batch(nnInput, nnLabels)
        dev_loss  = dev_loss/c
        logging.info("dev loss: {}".format(dev_loss))
                
                               
    def minibatch_iterate_devset(self, modelNames = None):
        """ Create based on sentence length mini-batches with approx. the same size. Sentences and 
        mini-batch chunks are shuffled and used to the train the model """
        
        if self.devSentenceLengthRanges == None:
            """ Create mini batch ranges """
            self.devSentenceLengthRanges = {}
            self.devMiniBatchRanges = {}            
            for modelName in self.modelNames:
                devData = self.data[modelName]['devMatrix']
                devData.sort(key=lambda x:len(x['tokens'])) #Sort dev matrix by sentence length
                devRanges = []
                oldSentLength = len(devData[0]['tokens'])            
                idxStart = 0
                
                #Find start and end of ranges with sentences with same length
                for idx in range(len(devData)):
                    sentLength = len(devData[idx]['tokens'])
                    
                    if sentLength != oldSentLength:
                        devRanges.append((idxStart, idx))
                        idxStart = idx
                    
                    oldSentLength = sentLength
                
                #Add last sentence
                devRanges.append((idxStart, len(devData)))
                
                
                #Break up ranges into smaller mini batch sizes
                miniBatchRanges = []
                for batchRange in devRanges:
                    rangeLen = batchRange[1]-batchRange[0]

                    bins = int(math.ceil(rangeLen/float(self.params['miniBatchSize'])))
                    binSize = int(math.ceil(rangeLen / float(bins)))
                    
                    for binNr in range(bins):
                        startIdx = binNr*binSize+batchRange[0]
                        endIdx = min(batchRange[1],(binNr+1)*binSize+batchRange[0])
                        miniBatchRanges.append((startIdx, endIdx))
                      
                self.devSentenceLengthRanges[modelName] = devRanges
                self.devMiniBatchRanges[modelName] = miniBatchRanges
                
        if modelNames == None:
            modelNames = self.modelNames
        #Shuffle dev data
        for modelName in modelNames:      
            #1. Shuffle sentences that have the same length
            x = self.data[modelName]['devMatrix']
            for dataRange in self.devSentenceLengthRanges[modelName]:
                for i in reversed(range(dataRange[0]+1, dataRange[1])):
                    # pick an element in x[:i+1] with which to exchange x[i]
                    j = random.randint(dataRange[0], i)
                    x[i], x[j] = x[j], x[i]
               
            #2. Shuffle the order of the mini batch ranges       
            random.shuffle(self.devMiniBatchRanges[modelName])
     
        
        #Iterate over the mini batch ranges
        if self.mainModelName != None:
            rangeLength = len(self.devMiniBatchRanges[self.mainModelName])
        else:
            rangeLength = min([len(self.devMiniBatchRanges[modelName]) for modelName in modelNames])

        
        batches = {}
        for idx in range(rangeLength):
            batches.clear()
            
            for modelName in modelNames:   
                devMatrix = self.data[modelName]['devMatrix']
                dataRange = self.devMiniBatchRanges[modelName][idx % len(self.devMiniBatchRanges[modelName])] 
                labels = np.asarray([devMatrix[idx][self.labelKeys[modelName]] for idx in range(dataRange[0], dataRange[1])])
                labels = np.expand_dims(labels, -1)
                
                
                batches[modelName] = [labels]
                
                for featureName in self.params['featureNames']:
                    inputData = np.asarray([devMatrix[idx][featureName] for idx in range(dataRange[0], dataRange[1])])
                    batches[modelName].append(inputData)
            
            yield batches      
          

    def minibatch_iterate_dataset(self, modelNames = None):
        """ Create based on sentence length mini-batches with approx. the same size. Sentences and 
        mini-batch chunks are shuffled and used to the train the model """
        
        if self.trainSentenceLengthRanges == None:
            """ Create mini batch ranges """
            self.trainSentenceLengthRanges = {}
            self.trainMiniBatchRanges = {}            
            for modelName in self.modelNames:
                trainData = self.data[modelName]['trainMatrix']
                trainData.sort(key=lambda x:len(x['tokens'])) #Sort train matrix by sentence length
                trainRanges = []
                oldSentLength = len(trainData[0]['tokens'])            
                idxStart = 0
                
                #Find start and end of ranges with sentences with same length
                for idx in range(len(trainData)):
                    sentLength = len(trainData[idx]['tokens'])
                    
                    if sentLength != oldSentLength:
                        trainRanges.append((idxStart, idx))
                        idxStart = idx
                    
                    oldSentLength = sentLength
                
                #Add last sentence
                trainRanges.append((idxStart, len(trainData)))
                
                
                #Break up ranges into smaller mini batch sizes
                miniBatchRanges = []
                for batchRange in trainRanges:
                    rangeLen = batchRange[1]-batchRange[0]

                    bins = int(math.ceil(rangeLen/float(self.params['miniBatchSize'])))
                    binSize = int(math.ceil(rangeLen / float(bins)))
                    
                    for binNr in range(bins):
                        startIdx = binNr*binSize+batchRange[0]
                        endIdx = min(batchRange[1],(binNr+1)*binSize+batchRange[0])
                        miniBatchRanges.append((startIdx, endIdx))
                      
                self.trainSentenceLengthRanges[modelName] = trainRanges
                self.trainMiniBatchRanges[modelName] = miniBatchRanges
                
        if modelNames == None:
            modelNames = self.modelNames
        #Shuffle training data
        for modelName in modelNames:      
            #1. Shuffle sentences that have the same length
            x = self.data[modelName]['trainMatrix']
            for dataRange in self.trainSentenceLengthRanges[modelName]:
                for i in reversed(range(dataRange[0]+1, dataRange[1])):
                    # pick an element in x[:i+1] with which to exchange x[i]
                    j = random.randint(dataRange[0], i)
                    x[i], x[j] = x[j], x[i]
               
            #2. Shuffle the order of the mini batch ranges       
            random.shuffle(self.trainMiniBatchRanges[modelName])
     
        
        #Iterate over the mini batch ranges
        if self.mainModelName != None:
            rangeLength = len(self.trainMiniBatchRanges[self.mainModelName])
        else:
            rangeLength = min([len(self.trainMiniBatchRanges[modelName]) for modelName in modelNames])

        
        batches = {}
        for idx in range(rangeLength):
            batches.clear()
            
            for modelName in modelNames:   
                trainMatrix = self.data[modelName]['trainMatrix']
                dataRange = self.trainMiniBatchRanges[modelName][idx % len(self.trainMiniBatchRanges[modelName])] 
                labels = np.asarray([trainMatrix[idx][self.labelKeys[modelName]] for idx in range(dataRange[0], dataRange[1])])
                labels = np.expand_dims(labels, -1)
                
                
                batches[modelName] = [labels]
                
                for featureName in self.params['featureNames']:
                    inputData = np.asarray([trainMatrix[idx][featureName] for idx in range(dataRange[0], dataRange[1])])
                    batches[modelName].append(inputData)
            
            yield batches   
            

        
    def storeResults(self, resultsFilepath):
        if resultsFilepath != None:
            directory = os.path.dirname(resultsFilepath)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            self.resultsSavePath = open(resultsFilepath, 'w')
        else:
            self.resultsSavePath = None
        
    def fit(self, epochs):
        if self.models is None:
            self.buildModel()

        total_train_time = 0
        max_dev_score = {modelName:0 for modelName in self.models.keys()}
        max_test_score = {modelName:0 for modelName in self.models.keys()}
        no_improvement_since = 0
        
        for epoch in range(epochs):      
            sys.stdout.flush()           
            logging.info("\n--------- Epoch %d -----------" % (epoch+1))
            
            start_time = time.time() 
            self.trainModel()
            
            
            time_diff = time.time() - start_time
            total_train_time += time_diff
            logging.info("%.2f sec for training (%.2f total)" % (time_diff, total_train_time))
            
            
            start_time = time.time() 
            for modelName in self.evaluateModelNames:
                logging.info("-- %s --" % (modelName))
                #self.models[modelName].evaluate(self.data[modelName]['devMatrix'][], self.data[modelName]['devMatrix'][])
                dev_score, test_score = self.computeScore(modelName, self.data[modelName]['devMatrix'], self.data[modelName]['testMatrix'])
                
                if dev_score > max_dev_score[modelName]:
                    max_dev_score[modelName] = dev_score
                    max_test_score[modelName] = test_score
                    no_improvement_since = 0

                    #Save the model
                    if self.modelSavePath != None:
                        self.saveModel(modelName, epoch, dev_score, test_score)
                else:
                    no_improvement_since += 1
                    
                    
                if self.resultsSavePath != None:
                    self.resultsSavePath.write("\t".join(map(str, [epoch + 1, modelName, dev_score, test_score, max_dev_score[modelName], max_test_score[modelName]])))
                    self.resultsSavePath.write("\n")
                    self.resultsSavePath.flush()
                
                logging.info("\nScores from epoch with best dev-scores:\n  Dev-Score: %.4f\n  Test-Score %.4f" % (max_dev_score[modelName], max_test_score[modelName]))
                logging.info("")
                
            logging.info("%.2f sec for evaluation" % (time.time() - start_time))
            
            if self.params['earlyStopping']  > 0 and no_improvement_since >= self.params['earlyStopping']:
                logging.info("!!! Early stopping, no improvement after "+str(no_improvement_since)+" epochs !!!")
                break
            
            
    def tagSentences(self, sentences):
        # Pad characters
        if 'characters' in self.params['featureNames']:
            self.padCharacters(sentences)

        labels = {}
        for modelName, model in self.models.items():
            paddedPredLabels = self.predictLabels(model, sentences)
            predLabels = []
            for idx in range(len(sentences)):
                unpaddedPredLabels = []
                for tokenIdx in range(len(sentences[idx]['tokens'])):
                    if sentences[idx]['tokens'][tokenIdx] != 0:  # Skip padding tokens
                        unpaddedPredLabels.append(paddedPredLabels[idx][tokenIdx])

                predLabels.append(unpaddedPredLabels)

            idx2Label = self.idx2Labels[modelName]
            labels[modelName] = [[idx2Label[tag] for tag in tagSentence] for tagSentence in predLabels]

        return labels
            
    
    def getSentenceLengths(self, sentences):
        sentenceLengths = {}
        for idx in range(len(sentences)):
            sentence = sentences[idx]['tokens']
            if len(sentence) not in sentenceLengths:
                sentenceLengths[len(sentence)] = []
            sentenceLengths[len(sentence)].append(idx)
        
        return sentenceLengths
    
    def predictLabels(self, model, sentences):
        predLabels = [None]*len(sentences)
        sentenceLengths = self.getSentenceLengths(sentences)
        
        for indices in sentenceLengths.values():   
            nnInput = []                  
            for featureName in self.params['featureNames']:
                inputData = np.asarray([sentences[idx][featureName] for idx in indices])
                nnInput.append(inputData)
            
            predictions = model.predict(nnInput, verbose=False)
            predictions = predictions.argmax(axis=-1) #Predict classes            
           
            
            predIdx = 0
            for idx in indices:
                predLabels[idx] = predictions[predIdx]    
                predIdx += 1   
        
        return predLabels
   
    def computeScore(self, modelName, devMatrix, testMatrix):
        #if self.labelKeys[modelName].endswith('_BIO') or self.labelKeys[modelName].endswith('_IOBES') or self.labelKeys[modelName].endswith('_IOB'):
        #    return self.computeF1Scores(modelName, devMatrix, testMatrix)
        #else:
        #    return self.computeAccScores(modelName, devMatrix, testMatrix)
        #return self.computeDisfluencyF1Scores(modelName, devMatrix, testMatrix)
        return self.computeComplexDisfluencyF1Scores(modelName, devMatrix, testMatrix)

    def computeF1Scores(self, modelName, devMatrix, testMatrix):
        #train_pre, train_rec, train_f1 = self.computeF1(modelName, self.datasets[modelName]['trainMatrix'])
        #print "Train-Data: Prec: %.3f, Rec: %.3f, F1: %.4f" % (train_pre, train_rec, train_f1)
        
        dev_pre, dev_rec, dev_f1 = self.computeF1(modelName, devMatrix)
        logging.info("Dev-Data: Prec: %.3f, Rec: %.3f, F1: %.4f" % (dev_pre, dev_rec, dev_f1))
        
        test_pre, test_rec, test_f1 = self.computeF1(modelName, testMatrix)
        logging.info("Test-Data: Prec: %.3f, Rec: %.3f, F1: %.4f" % (test_pre, test_rec, test_f1))
        
        return dev_f1, test_f1
    
    def computeDisfluencyF1Scores(self, modelName, devMatrix, testMatrix):
        train_f1 = self.computeDisfluencyF1(modelName, self.data[modelName]['trainMatrix'])
        dev_f1 = self.computeDisfluencyF1(modelName, devMatrix)
        test_f1 = self.computeDisfluencyF1(modelName, testMatrix)
        
        logging.info("Train-Data F1: %.4f" % (train_f1))
        logging.info("Dev-Data F1: %.4f" % (dev_f1))
        logging.info("Test-Data F1: %.4f" % (test_f1))
        
        return dev_f1, test_f1
        
    def computeComplexDisfluencyF1Scores(self, modelName, devMatrix, testMatrix):
        #train_f1 = self.computeComplexDisfluencyF1(modelName, self.data[modelName]['trainMatrix'])
        dev_f1 = self.computeComplexDisfluencyF1(modelName, devMatrix)
        test_f1 = self.computeComplexDisfluencyF1(modelName, testMatrix)
        
        #logging.info("Train-Data F1: %.4f" % (train_f1))
        logging.info("Dev-Data F1: %.4f" % (dev_f1))
        logging.info("Test-Data F1: %.4f" % (test_f1))
        
        return dev_f1, test_f1
    
    def computeAccScores(self, modelName, devMatrix, testMatrix):
        train_acc = self.computeAcc(modelName, self.data[modelName]['trainMatrix'])
        dev_acc = self.computeAcc(modelName, devMatrix)
        test_acc = self.computeAcc(modelName, testMatrix)
        
        logging.info("Train-Data: Accuracy: %.4f" % (train_acc))
        logging.info("Dev-Data: Accuracy: %.4f" % (dev_acc))
        logging.info("Test-Data: Accuracy: %.4f" % (test_acc))
        
        return dev_acc, test_acc   
        
        
    def computeF1(self, modelName, sentences):
        labelKey = self.labelKeys[modelName]
        model = self.models[modelName]
        idx2Label = self.idx2Labels[modelName]
        
        correctLabels = [sentences[idx][labelKey] for idx in range(len(sentences))]
        predLabels = self.predictLabels(model, sentences) 

        labelKey = self.labelKeys[modelName]
        encodingScheme = labelKey[labelKey.index('_')+1:]
        
        pre, rec, f1 = BIOF1Validation.compute_f1(predLabels, correctLabels, idx2Label, 'O', encodingScheme)
        pre_b, rec_b, f1_b = BIOF1Validation.compute_f1(predLabels, correctLabels, idx2Label, 'B', encodingScheme)
        
        if f1_b > f1:
            logging.debug("Setting wrong tags to B- improves from %.4f to %.4f" % (f1, f1_b))
            pre, rec, f1 = pre_b, rec_b, f1_b
        
        return pre, rec, f1
    
    def computeDisfluencyF1(self, modelName, sentences):
        reparandum = ["BE", "IE", "IP", "BE_IP", "C_IP", "C_IE"]
        rm_mapping = []
        for rm in reparandum:
            rm_mapping.append(self.mappings['disfluency'][rm])

        correctLabels = [sentences[idx][self.labelKeys[modelName]] for idx in range(len(sentences))]
        predLabels = self.predictLabels(self.models[modelName], sentences)

        tp = 0
        fp = 0
        fn = 0

        for sentenceId in range(len(correctLabels)):
            for tokenId in range(len(correctLabels[sentenceId])):
                if correctLabels[sentenceId][tokenId] in rm_mapping and predLabels[sentenceId][tokenId] in rm_mapping:
                    tp += 1
                elif correctLabels[sentenceId][tokenId] not in rm_mapping and predLabels[sentenceId][tokenId] in rm_mapping:
                    fp += 1
                elif correctLabels[sentenceId][tokenId] in rm_mapping and predLabels[sentenceId][tokenId] not in rm_mapping:
                    fn += 1
                else:
                    pass
        nc = tp
        nt = tp + fn
        nm = tp + fp
        
        precision = nc/nm
        recall = nc/nt
        fscore = (2 * precision * recall) / ( precision + recall)
        
        return fscore
    
    def computeComplexDisfluencyF1(self, modelName, sentences):
        reparandum = ["BE", "IE", "IP", "BE_IP", "C_IP", "C_IE"]
        rm_mapping = []
        for rm in reparandum:
            rm_mapping.append(self.mappings['disfluency'][rm])
        BE_IP = self.mappings['disfluency']['BE_IP']
        C = self.mappings['disfluency']['C']

        correctLabels = [sentences[idx][self.labelKeys[modelName]] for idx in range(len(sentences))]
        token_ids = [sentences[idx]['tokens'] for idx in range(len(sentences))]
        predLabels = self.predictLabels(self.models[modelName], sentences)

        tp = 0
        fp = 0
        fn = 0
        
        one_word_rep = 0

        for sentenceId in range(len(correctLabels)):
            for tokenId in range(len(correctLabels[sentenceId])):
                # compute F-score only on disfluencies that are not one-word repetitions
                if (tokenId+1) < len(correctLabels[sentenceId]) and correctLabels[sentenceId][tokenId] == BE_IP and correctLabels[sentenceId][tokenId+1] == C and token_ids[sentenceId][tokenId] == token_ids[sentenceId][tokenId+1]:
                    pass
                elif correctLabels[sentenceId][tokenId] in rm_mapping and predLabels[sentenceId][tokenId] in rm_mapping:
                    tp += 1
                elif correctLabels[sentenceId][tokenId] not in rm_mapping and predLabels[sentenceId][tokenId] in rm_mapping:
                    fp += 1
                elif correctLabels[sentenceId][tokenId] in rm_mapping and predLabels[sentenceId][tokenId] not in rm_mapping:
                    fn += 1
                else:
                    pass
        nc = tp
        nt = tp + fn
        nm = tp + fp
        try:
            precision = nc/nm
            recall = nc/nt
            fscore = (2 * precision * recall) / ( precision + recall)
        except:
            fscore = 0
        
        return fscore
    
    def computeAcc(self, modelName, sentences):
        correctLabels = [sentences[idx][self.labelKeys[modelName]] for idx in range(len(sentences))]
        predLabels = self.predictLabels(self.models[modelName], sentences) 
        
        numLabels = 0
        numCorrLabels = 0
        for sentenceId in range(len(correctLabels)):
            for tokenId in range(len(correctLabels[sentenceId])):
                numLabels += 1
                if correctLabels[sentenceId][tokenId] == predLabels[sentenceId][tokenId]:
                    numCorrLabels += 1

  
        return numCorrLabels/float(numLabels)
    
    def padCharacters(self, sentences):
        """ Pads the character representations of the words to the longest word in the dataset """
        #Find the longest word in the dataset
        maxCharLen = self.params['maxCharLength']
        if maxCharLen <= 0:
            for sentence in sentences:
                for token in sentence['characters']:
                    maxCharLen = max(maxCharLen, len(token))
          

        for sentenceIdx in range(len(sentences)):
            for tokenIdx in range(len(sentences[sentenceIdx]['characters'])):
                token = sentences[sentenceIdx]['characters'][tokenIdx]

                if len(token) < maxCharLen: #Token shorter than maxCharLen -> pad token
                    sentences[sentenceIdx]['characters'][tokenIdx] = np.pad(token, (0,maxCharLen-len(token)), 'constant')
                else: #Token longer than maxCharLen -> truncate token
                    sentences[sentenceIdx]['characters'][tokenIdx] = token[0:maxCharLen]
    
        self.maxCharLen = maxCharLen
        
    def addTaskIdentifier(self):
        """ Adds an identifier to every token, which identifies the task the token stems from """
        taskID = 0
        for modelName in self.modelNames:
            dataset = self.data[modelName]
            for dataName in ['trainMatrix', 'devMatrix', 'testMatrix']:            
                for sentenceIdx in range(len(dataset[dataName])):
                    dataset[dataName][sentenceIdx]['taskID'] = [taskID] * len(dataset[dataName][sentenceIdx]['tokens'])
            
            taskID += 1


    def saveModel(self, modelName, epoch, dev_score, test_score):
        import json
        import h5py

        if self.modelSavePath == None:
            raise ValueError('modelSavePath not specified.')

        savePath = self.modelSavePath.replace("[DevScore]", "%.4f" % dev_score).replace("[TestScore]", "%.4f" % test_score).replace("[Epoch]", str(epoch+1)).replace("[ModelName]", modelName)

        directory = os.path.dirname(savePath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.isfile(savePath):
            logging.info("Model "+savePath+" already exists. Model will be overwritten")

        self.models[modelName].save(savePath, True)

        with h5py.File(savePath, 'a') as h5file:
            h5file.attrs['mappings'] = json.dumps(self.mappings)
            h5file.attrs['params'] = json.dumps(self.params)
            h5file.attrs['modelName'] = modelName
            h5file.attrs['labelKey'] = self.datasets[modelName]['label']




    @staticmethod
    def loadModel(modelPath):
        import h5py
        import json
        from .keraslayers.ChainCRF import create_custom_objects

        model = keras.models.load_model(modelPath, custom_objects=create_custom_objects())

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
        return bilstm
