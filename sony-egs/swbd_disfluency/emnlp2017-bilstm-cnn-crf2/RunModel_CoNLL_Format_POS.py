#!/usr/bin/python
# This scripts loads a pretrained model and a input file in CoNLL format (each line a token, sentences separated by an empty line).
# The input sentences are passed to the model for tagging. Prints the tokens and the tags in a CoNLL format to stdout
# Usage: python RunModel_ConLL_Format.py modelPath inputPathToConllFile
# For pretrained models see docs/
from __future__ import print_function
from util.preprocessing import readCoNLL, createMatrices, addCharInformation, addCasingInformation, addProsodicInformation
from neuralnets.BiLSTM import BiLSTM
import pickle as pkl
import sys
import logging


if len(sys.argv) < 3:
    print("Usage: python RunModel_CoNLL_Format.py modelPath inputPathToConllFile")
    exit()

modelPath = sys.argv[1]
inputPath = sys.argv[2]
dataset = inputPath.split("/")[1]
#inputColumns = {0: "tokens"}
#inputColumns = {4: "tokens"}
#inputColumns = {4:'tokens', 5:'disfluency', 6:'pos', 7:'filler', 8:'discourse', 9:'edit'}
if dataset == "disfluency":
    inputColumns = {4:'tokens', 5:'disfluency', 6:'pos', 7:'filler', 8:'discourse', 9:'edit'}
elif dataset == "disfluency_silver":
    inputColumns = {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'}
elif dataset == "disfluency_pitch" or dataset == "disfluency_energy" or dataset == 'disfluency_formants' or dataset == "test_disfluency":
    inputColumns = {0:'utt_id', 1:'tokens', 2:'disfluency', 3:'pos'}
elif dataset == "disfluency_duration" or dataset == "disfluency_duration_fluent_only" or dataset == 'disfluency_prosody':
    inputColumns = {0: 'utt_id', 1:'tokens', 2:'disfluency', 3:'pos', 4:'word_dur_phone', 5:'word_dur_word', 6:'pause'}
elif dataset == "kaldi_test":
    inputColumns = {0: 'utt_id', 1:'tokens', 2:'disfluency', 3:'word_dur_phone', 4:'word_dur_word', 5:'pause'}
#inputColumns = {2:'tokens'}

# :: Prepare the input ::
sentences = readCoNLL(inputPath, inputColumns)
addCharInformation(sentences)
addCasingInformation(sentences)
d, dataset, partition = inputPath.split("/")
partition = partition.replace(".txt", "")
try:
    pkl_f = open(d + "/" + dataset + "/" + partition+"_prosody_feats.pkl", 'rb')
    prosody = pkl.load(pkl_f, encoding='iso-8859-1')
    addProsodicInformation(sentences,prosody)
except:
    pass

# :: Load the model ::
lstmModel = BiLSTM.loadModel(modelPath)
dataMatrix = createMatrices(sentences, lstmModel.mappings, True)

# :: Tag the input ::
tags = lstmModel.tagSentences(dataMatrix)


# :: Output to stdout ::
for sentenceIdx in range(len(sentences)):
    tokens = sentences[sentenceIdx]['tokens']

    for tokenIdx in range(len(tokens)):
        tokenTags = []
        for modelName in sorted(tags.keys()):
            tokenTags.append(tags[modelName][sentenceIdx][tokenIdx])

        print("%s\t%s" % (tokens[tokenIdx], "\t".join(tokenTags)))
    print("")
