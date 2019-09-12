"""
Run this with python3, pickle file will be less than a third of the size compared to python2

This script can be used to write prosodic features for kaldi output into pickle files.
The prosodic features are pitch, energy and formants by default since they showed an effect in disfluency detection for silver transcripts.

The script has two conditions: test=True and test=False. 
If test is True, pickle files are generated for the test utterances of ALL kaldi outputs.
If test is False, pickle files are generated for train, dev and test of ONE kaldi output.

Usage:
  python load_prosodic_data_kaldi.py test=[True,False] output_dir
  e.g.
  python load_prosodic_data_kaldi.py test=False data/7_0.0
  python load_prosodic_data_kaldi.py test=True data/kaldi_test
"""

import numpy as np
import sys
import ast
import pickle as pkl
import collections
import os

f_pitch = True
f_energy = True
f_formants = True

if sys.argv[1] == "test=True":
    test = True
elif sys.argv[1] == "test=False":
    test = False


max_word_length = 422
num_feats = 0


# Pitch and energy features are computed with Kaldi with a window length of 25ms and a shift of 10 ms
# this means that each value corresponds to a 10 ms frame
# Since window length > shift, the last two frames receive no value
# Therefore, two zero-padded frames are added to match vector length with time stamps as given in MS-State transcripts
if f_pitch == True:
    print("Reading pitch features...")
    #pitch_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/F0/pitch_feats", "r")
    pitch_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/F0/pitch_feats", "r")
    num_feats += 3
    utt_id = ""
    pitch = {}
    for line in pitch_feats:
        line = line.split()
        if line[1] == "[":
            if utt_id != "":
                # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
                pitch[utt_id].append([0.0, 0.0, 0.0])
                pitch[utt_id].append([0.0, 0.0, 0.0])
            utt_id = line[0]
            pitch[utt_id] = []
        else:
            p1 = float(line[0])
            p2 = float(line[1])
            p3 = float(line[2])
            l = [p1,p2,p3]
            pitch[utt_id].append(l)
    # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
    pitch[utt_id].append([0.0, 0.0, 0.0])
    pitch[utt_id].append([0.0, 0.0, 0.0])

"""
# highest total energy in corpus is 25.42658
max_energy = 26
if f_energy == True:
    print("Reading energy features...")
    #energy_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy", "r")
    energy_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy", "r")
    num_feats += 3
    utt_id = ""
    energy = {}
    for line in energy_feats:
        line = line.split()
        if line[1] == "[":
            if utt_id != "":
                # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
                energy[utt_id].append([0.0, 0.0, 0.0])
                energy[utt_id].append([0.0, 0.0, 0.0])
            utt_id = line[0]
            energy[utt_id] = []
        else:
            e = float(line[0])
            total = e/max_energy
            fbank_low = np.log(np.sum(np.exp(np.array(line[1:21], dtype='float32'))))/e
            fbank_high = np.log(np.sum(np.exp(np.array(line[21:41], dtype='float32'))))/e
            energy[utt_id].append([total, fbank_low, fbank_high])
    # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
    energy[utt_id].append([0.0, 0.0, 0.0])
    energy[utt_id].append([0.0, 0.0, 0.0])
"""

if f_energy == True:
    print("Reading energy features...")
    energy_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy_preprocessed", "r")
    num_feats += 3
    utt_id = ""
    energy = {}
    for line in energy_feats:
        line = line.split()
        if line[1] == "[":
            if utt_id != "":
                # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
                energy[utt_id].append([0.0, 0.0, 0.0])
                energy[utt_id].append([0.0, 0.0, 0.0])
            utt_id = line[0]
            energy[utt_id] = []
        else:
            total = float(line[0])
            e_low = float(line[1])
            e_high = float(line[2])
            energy[utt_id].append([total, e_low, e_high])
    # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
    energy[utt_id].append([0.0, 0.0, 0.0])
    energy[utt_id].append([0.0, 0.0, 0.0])

"""
# For formants, no zero padding is necessary since DeepFormants derives one value for each 10 ms frame
max_f1 = 958.8
max_f2 = 2523.1
max_f3 = 3218.0
max_f4 = 4207.5
if f_formants == True:
    print("Reading formant features...")
    #formants_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/formants/formant_feats")
    formants_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/formants/formant_feats")
    num_feats += 4
    formants = {}
    for line in formants_feats:
        utt_id, F1, F2, F3, F4 = line.split(",")
        #skip header
        if utt_id != "NAME":
            utt_id = utt_id.replace("switchboard_data_trim", "").strip("./")[:15]
            F4 = F4.strip()
            if utt_id not in formants:
                formants[utt_id] = []
            F1 = float(F1)/max_f1
            F2 = float(F2)/max_f2
            F3 = float(F3)/max_f3
            F4 = float(F4)/max_f4
            formants[utt_id].append([F1, F2, F3, F4])
"""
if f_formants == True:
    print("Reading formant features...")
    formants_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/formants/formant_feats_preprocessed")
    num_feats += 4
    formants = {}
    for line in formants_feats:
        utt_id, F1, F2, F3, F4 = line.split()
        if utt_id not in formants:
            formants[utt_id] = []
        formants[utt_id].append([F1, F2, F3, F4])


#kaldi_directory = "/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/data/kaldi"
kaldi_directory = "/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/data/kaldi"
path = sys.argv[2]
print("Gathering kaldi files")
if test == True:
    print(kaldi_directory)
    kaldi_files = []
    for r, d, f in os.walk(kaldi_directory):
        for kaldi_file in f:
            if ".txt" not in kaldi_file and "score" in kaldi_file:
                kaldi_files.append(kaldi_file)
else:
    version = path.split("/")[1]
    kaldi_file = "score_" + version
    kaldi_files = [kaldi_file]

kaldi_files = ["score_15_0.0", "score_16_0.0", "score_16_0.5", "score_17_0.0", "score_8_0.5"]

for kaldi_file in kaldi_files:
    print("Gathering prosodic features for {}".format(kaldi_file))
    kaldi = open(kaldi_directory + "/" + kaldi_file, "r")
    if test == True:
        version_name = kaldi_file.replace("score", "")
    train_prosody_feats = {}
    dev_prosody_feats = {}
    test_prosody_feats = {}
    count = 1
    prev_utt_id = "blub"
    utts = []
    for line in kaldi:
        try:
            utt_id, file_id, word, tag, start, end = line.split()
        except:
            continue
        end = int(end.strip())
        start = int(start)
        if prev_utt_id == "blub":
            prev_utt_id = utt_id
            utt = []
        elif utt_id != prev_utt_id:
            utt = np.array(utt, dtype='float32')
            utt_number = int(prev_utt_id[2:6])
            if test == True:
                if utt_number > 3999 and utt_number < 4200:
                    test_prosody_feats[prev_utt_id] = utt
                elif utt_number > 4499:
                    dev_prosody_feats[prev_utt_id] = utt
            else:
                if utt_number < 4000:
                    train_prosody_feats[prev_utt_id] = utt
                elif utt_number > 4499:
                    dev_prosody_feats[prev_utt_id] = utt
                elif utt_number > 3999 and utt_number < 4200:
                    test_prosody_feats[prev_utt_id] = utt
            prev_utt_id = utt_id
            utt = []
        w = np.zeros((max_word_length, num_feats))
        if f_pitch == True:
            w[0:end-start, 0:3] = np.array(pitch[utt_id][start:end], dtype='float32')
            if f_energy == True:
                w[0:end-start, 3:6] = np.array(energy[utt_id][start:end], dtype='float32')
                if f_formants == True:
                    try:
                        w[0:end-start, 6:10] = np.array(formants[utt_id][start:end], dtype='float32')
                    except:
                        w[0:end-start-1, 6:10] = np.array(formants[utt_id][start:end-1], dtype='float32')
        utt.append(w)
    #last line of kaldi_file
    utt = np.array(utt, dtype='float32')
    utt_number = int(utt_id[2:6])
    if test == True:
        if utt_number > 3999 and utt_number < 4200:
            test_prosody_feats[utt_id] = utt
        elif utt_number > 4499:
            dev_prosody_feats[utt_id] = utt
    else:
        if utt_number < 4000:
            train_prosody_feats[utt_id] = utt
        elif utt_number > 4499:
            dev_prosody_feats[utt_id] = utt
        elif utt_number > 3999 and utt_number < 4200:
            test_prosody_feats[utt_id] = utt

    print("Writing pickle file for {}".format(kaldi_file))
    if test == True:
        #output = open("{}/test{}_prosody_feats.pkl".format(path,version_name), "wb")
        output2 = open("{}/dev{}_prosody_feats.pkl".format(path,version_name), "wb")
        #pkl.dump(test_prosody_feats, output)
        #output.close()
        pkl.dump(dev_prosody_feats, output2)
        output2.close()
    else:
        output1 = open("{}/train_prosody_feats.pkl".format(path), "wb")
        output2 = open("{}/dev_prosody_feats.pkl".format(path), "wb")
        output3 = open("{}/test_prosody_feats.pkl".format(path), "wb")
        pkl.dump(train_prosody_feats, output1)
        output1.close()
        pkl.dump(dev_prosody_feats, output2)
        output2.close()
        pkl.dump(test_prosody_feats, output3)
        output3.close()

