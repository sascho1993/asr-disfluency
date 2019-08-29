from __future__ import division
import sys

gold_file = open(sys.argv[1], "r")

word = []
gold = []
for line in gold_file:
    line = line.split('\t')
    try:
        gold.append(line[5].strip())
        word.append(line[4].strip())
    except:
        pass


word_rep = 0
tp = 0
all_disfl = 0

reparandum = ["BE", "IE", "IP", "BE_IP", "C_IP", "C_IE"]

for i in range(len(gold)-1):
    if word[i] == word[i+1]:
        word_rep += 1
        if gold[i] in reparandum:
            tp += 1
            all_disfl += 1
    else:
        if gold[i] in reparandum:
            all_disfl += 1

print ("word_repetitions: ", word_rep)
print ("true positives: ", tp)
print ("all disfluencies: ", all_disfl)
            
