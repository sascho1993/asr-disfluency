"""
Split switchboard file into train, dev and test files depending on utterance number
"""

import sys

f = open(sys.argv[1], "r")
path = sys.argv[2].strip("/")

train = open("{}/train.txt".format(path), "w")
dev = open("{}/dev.txt".format(path), "w")
test = open("{}/test.txt".format(path), "w")

train_marker = False
dev_marker = False
test_marker = False
heldout = False

for l in f:
    line = l.split('\t')
    try:
        file_id = line[0][2:6]
        if int(file_id) < 4000:
            train_marker = True
            train.write(l)
        elif int(file_id) > 4499:
            dev_marker = True
            dev.write(l)
        elif int(file_id) > 3999 and int(file_id) < 4200:
            test_marker = True
            test.write(l)
        else:
            heldout = True
    except:
        if train_marker == True:
            train_marker = False
            train.write("\n")
        elif dev_marker == True:
            dev_marker = False
            dev.write("\n")
        elif test_marker == True:
            test_marker = False
            test.write("\n")
        else:
            heldout = False
        
