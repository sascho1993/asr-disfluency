from __future__ import division
import sys

gold_file = open(sys.argv[1], "r")
prediction_file_name = sys.argv[2]
prediction_file = open(prediction_file_name, "r")

gold = []
for line in gold_file:
    line = line.split('\t')
    try:
        gold.append(line[2].strip())
    except:
        pass


prediction = []
word = []
for line in prediction_file:
    line = line.split('\t')
    try:
        prediction.append(line[1].strip())
        word.append(line[0].strip())
    except:
        pass


reparandum = ["BE", "IE", "IP", "BE_IP", "C_IP", "C_IE"]


print ("==================================================================================================")
print (prediction_file_name)
print ("==================================================================================================")
tp = 0
fp = 0
fn = 0

for i in range(len(gold)):
    if gold[i] in reparandum and prediction[i] in reparandum:
        tp += 1
    elif gold[i] not in reparandum and prediction[i] in reparandum:
        fp += 1
    elif gold[i] in reparandum and prediction[i] not in reparandum:
        fn += 1
    else:
        pass

print ("General Evaluation with all disfluency types")

print ("tp: ", tp)
print ("fn: ", fn)
print ("fp: ", fp)
#print ("simple disfluencies: ", simple_disfluencies)
#print ("simple non-repetitions: ", simple_non_repetitions)

nc = tp
nt = tp + fn
nm = tp + fp


precision = nc/nm
recall = nc/nt
fscore = (2 * precision * recall) / ( precision + recall)

print ("precision: ", precision)
print ("recall: ", recall)
print ("F1: ", fscore)
