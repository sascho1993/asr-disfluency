# This script trains the BiLSTM-CRF architecture for part-of-speech tagging using
# the universal dependency dataset (http://universaldependencies.org/).
# The code use the embeddings by Komninos et al. (https://www.cs.york.ac.uk/nlp/extvec/)
from __future__ import print_function
import os
import logging
import sys
from neuralnets.BiLSTM import BiLSTM
from util.preprocessing import perpareDataset, loadDatasetPickle
#from util.preprocessing_with_prosody import perpareDataset as prosody_perpareDataset
#from util.preprocessing_with_prosody import loadDatasetPickle as prosody_loadDatasetPickle
import subprocess
import re
import argparse


# :: Change into the working dir of the script ::
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# :: Logging level ::
loggingLevel = logging.INFO
logger = logging.getLogger()
logger.setLevel(loggingLevel)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(loggingLevel)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# :: Parse arguments ::
parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, dest='dataset', required=True)
parser.add_argument("--LSTMSize", type=int,  dest='LSTMSize', required=True, nargs='*')
parser.add_argument("--dropout", type=float, dest='dropout', required=True, nargs='*')
parser.add_argument("--seed", type=int, dest='seed', default=None)
parser.add_argument("--featureNames", type=str, dest='featureNames', required=False, nargs='*')
parser.add_argument("--optimizer", type=str, dest='optimizer', default = "adam")
parser.add_argument("--miniBatchSize", type=int, dest='miniBatchSize', default = 32)
parser.add_argument("--prosodyEmbeddings", type=str, dest='prosodyEmbeddings', default = 'None')
parser.add_argument("--prosodyLSTMSize", type=int, dest='prosodyLSTMSize', default = None)
parser.add_argument("--prosodyFilterSize", type=int, dest='prosodyFilterSize', default = None)
parser.add_argument("--expName", type=str, dest='expName', required=True)
args = parser.parse_args()
######################################################
#
# Data preprocessing
#
######################################################

if args.dataset == "disfluency":
    datasets = {
        'disfluency':
            {'columns': {4:'tokens', 5:'disfluency', 6:'pos', 7:'filler', 8:'discourse', 9:'edit'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
elif args.dataset == "disfluency_silver":
    datasets = {
        'disfluency_silver':
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 0
elif args.dataset == "disfluency_pitch":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 3
    pretrainedWeights = "pitch"
elif args.dataset == "disfluency_energy":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 3
    pretrainedWeights = "energy"
elif args.dataset == "disfluency_pitch_energy":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 6
elif args.dataset == "disfluency_raw_pitch":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 1
elif args.dataset == "disfluency_mean_energy":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 1
elif args.dataset == "disfluency_duration" or args.dataset == "disfluency_duration_fluent_only":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos', 4:'word_dur_phone', 5:'word_dur_word', 6:'pause'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 0
    pretrainedWeights = None
elif args.dataset == "disfluency_prosody" or args.dataset == "7_0.0" or args.dataset == "17_1.0":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos', 4:'word_dur_phone', 5:'word_dur_word', 6:'pause'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 10
    pretrainedWeights = "pitch_energy_formants"
elif args.dataset == "disfluency_formants":
    datasets = {
        args.dataset:
            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'},
             'label': 'disfluency',                     #Which column we like to predict
             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
    }
    numberProsodyFeatures = 4
    pretrainedWeights = "formants"
#elif args.dataset == "7_0.0":
#    datasets = {
#        args.dataset:
#            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos', 4:'word_dur_phone', 5:'word_dur_word', 6:'pause'},
#             'label': 'disfluency',                     #Which column we like to predict
#             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
#             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
#    }
#    numberProsodyFeatures = 10
#    pretrainedWeights = "kaldi_prosody_7_0.0"
#elif args.dataset == "17_1.0":
#    datasets = {
#        args.dataset:
#            {'columns': {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos', 4:'word_dur_phone', 5:'word_dur_word', 6:'pause'},
#             'label': 'disfluency',                     #Which column we like to predict
#             'evaluate': True,                   #Should we evaluate on this task? Set true always for single task setups
#             'commentSymbol': None}              #Lines in the input data starting with this string will be skipped. Can be used to skip comments
#    }
#    numberProsodyFeatures = 10
#    pretrainedWeights = "kaldi_prosody_17_1.0"
else:
    print ("unknown dataset")
    sys.exit


# :: Path on your computer to the word embeddings. Embeddings by Komninos et al. will be downloaded automatically ::
embeddingsPath = 'komninos_english_embeddings.txt'

# :: Prepares the dataset to be used with the LSTM-network. Creates and stores cPickle files in the pkl/ folder ::
#if args.dataset == "disfluency" or args.dataset == "disfluency_silver":
#    pickleFile = perpareDataset(embeddingsPath, datasets)
#else:
#    pickleFile = prosody_perpareDataset(embeddingsPath, datasets)
pickleFile = perpareDataset(embeddingsPath, datasets)

######################################################
#
# The training of the network starts here
#
######################################################


#Load the embeddings and the dataset
embeddings, mappings, data = loadDatasetPickle(pickleFile)

# Dropout
if len(args.dropout) == 1:
    dropout = args.dropout[0]
elif len(args.dropout) > 2:
    print("For naive dropout give one value, for variational dropout 2 values")
    sys.exit()
else:
    dropout = args.dropout

if args.featureNames == None:
    featureNames = []
else:
    featureNames = args.featureNames

# Overriding default parameters
params = {'classifier': ['CRF'], 'LSTM-Size': args.LSTMSize, 'dropout': dropout, 'seed': args.seed, 'featureNames': featureNames, 'optimizer': args.optimizer, 'miniBatchSize': args.miniBatchSize, 'prosodyEmbeddings' : args.prosodyEmbeddings, 'numberProsodyFeatures' : numberProsodyFeatures, 'pretrainedWeights' : pretrainedWeights,'prosodyFilterSize': args.prosodyFilterSize, 'prosodyLSTMSize': args.prosodyLSTMSize}

# Converting parameters to string
lstm_size = ""
for i in params['LSTM-Size']:
    lstm_size = lstm_size + "," + str(i)
lstm_size = lstm_size.strip(",")

dropout_rate = ""
if isinstance(params['dropout'], (list, tuple)):
    for i in params['dropout']:
        dropout_rate = dropout_rate + "," + str(i)
else:
    dropout_rate = str(params['dropout'])
dropout_rate = dropout_rate.strip(",")

features = ""
for i in params['featureNames']:
    features = features + "," + str(i)
features = features.strip(",")
if params['featureNames'] == []:
    features = 'None'




model = BiLSTM(params)
model.setMappings(mappings, embeddings)
model.setDataset(datasets, data)
#model.storeResults('results/unidep_pos_results.csv') #Path to store performance scores for dev / test
if params['prosodyEmbeddings'] == 'cnn':
    model.modelSavePath = "models/{5}/[ModelName]_f{3}_o{4}_lstm{0}_dropout{1}_mb{6}_filter{7}_seed{2}/[ModelName]_f{3}_lstm{0}_dropout{1}_mb{6}_filter{7}_seed{2}_[DevScore]_[TestScore]_[Epoch].h5".format(lstm_size, dropout_rate, params['seed'], features, params['optimizer'], args.expName, params['miniBatchSize'], params['prosodyFilterSize']) #Path to store models
elif params['prosodyEmbeddings'] == 'lstm':
    model.modelSavePath = "models/{5}/[ModelName]_f{3}_o{4}_lstm{0}_dropout{1}_mb{6}_prosodyLSTM{7}_seed{2}/[ModelName]_f{3}_lstm{0}_dropout{1}_mb{6}_prosodyLSTM{7}_seed{2}_[DevScore]_[TestScore]_[Epoch].h5".format(lstm_size, dropout_rate, params['seed'], features, params['optimizer'], args.expName, params['miniBatchSize'], params['prosodyLSTMSize']) #Path to store models
else:
    model.modelSavePath = "models/{5}/[ModelName]_f{3}_o{4}_lstm{0}_dropout{1}_mb{6}_seed{2}/[ModelName]_f{3}_lstm{0}_dropout{1}_mb{6}_seed{2}_[DevScore]_[TestScore]_[Epoch].h5".format(lstm_size, dropout_rate, params['seed'], features, params['optimizer'], args.expName, params['miniBatchSize']) #Path to store models

model.fit(epochs=50)



