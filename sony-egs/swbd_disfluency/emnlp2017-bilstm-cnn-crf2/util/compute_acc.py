from __future__ import division
import sys

gold_file = open(sys.argv[1], "r")
prediction_file = open(sys.argv[2], "r")

gold = []
for line in gold_file:
    line = line.split('\t')
    try:
        gold.append(line[5].strip())
    except:
        #pass
        gold.append("")
 
prediction = []
for line in prediction_file:
    line = line.split('\t')
    try:
        prediction.append(line[1].strip())
    except:
        #pass
        prediction.append("")

numLabels = 0
numCorrLabels = 0
for tokenId in range(len(gold)):
    if gold[tokenId] != "":
        numLabels += 1
        if gold[tokenId] == prediction[tokenId]:
            numCorrLabels += 1

acc = numCorrLabels/numLabels

print (acc)
