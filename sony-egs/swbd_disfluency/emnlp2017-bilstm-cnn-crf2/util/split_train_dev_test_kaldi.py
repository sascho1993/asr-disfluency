"""
Split kaldi outputs in kaldi_test into train, dev and test sets
"""

import sys

kaldi_file = sys.argv[1]
f = open(kaldi_file, "r")
# e.g. 8_0.0
version = kaldi_file.split("/")[-1].replace("score", "").replace(".done", "").strip("_")
path = sys.argv[2].strip("/")

#train = open("{}/train.txt".format(path), "w")
dev = open("{}/dev_{}.txt".format(path, version), "w")
test = open("{}/test_{}.txt".format(path, version), "w")
#heldout_f = open("{}/heldout_{}.txt".format(path, version), "w")

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
            #train.write(l)
        elif int(file_id) > 4499:
            dev_marker = True
            dev.write(l)
        elif int(file_id) > 3999 and int(file_id) < 4200:
            test_marker = True
            test.write(l)
        else:
            heldout = True
            #heldout_f.write(l)
    except:
        if train_marker == True:
            train_marker = False
            #train.write("\n")
        elif dev_marker == True:
            dev_marker = False
            dev.write("\n")
        elif test_marker == True:
            test_marker = False
            test.write("\n")
        else:
            heldout = False
            #heldout_f.write("\n")

        
