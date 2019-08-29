"""
Run this with python3, pickle file will be less than a third of the size compared to python2

Scripts reads in ms_silver_word_time_stamps and computes a matrix with prosodic features for each word.
The matrices are written into pickle files, one per train, dev and test set.
Depending on which features are specified, the files are automatically written into the correct data directory,
e.g. if only formants are specified, the directory is data/disfluency_formants.

Usage: python load_prosodic_data.py [feature]+
"""

import numpy as np
import sys
import ast
import pickle as pkl
import collections

test = False
f_pitch = False
f_raw_pitch = False
f_energy = False
f_mean_energy = False
f_formants = False

# Available features:
# pitch - kaldi pitch features resulting from compute-and-process-kaldi-pitch-feats, already normalised
# raw_pitch - raw pitch feature resulting from compute-kaldi-pitch-feats that is normalised by overall maximum pitch (obsolete if pitch is used)
# energy - kaldi fbank features with 40 filters; three features are computed:
#     - overall energy normalised by overall max energy
#     - mean energy of 20 lowest filters normalised by overall energy
#     - mean energy of 20 highest filters normalised by overall energy
# formants - first 4 formants extracted with DeepFormants; each normalised by the respective global maximum
if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("You must choose at least one of there following prosodic features: pitch, raw_pitch, energy, formants")
    sys.exit()
else:
    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ["pitch", "Pitch"]:
            f_pitch = True
        elif sys.argv[i] in ["rawPitch", "rawpitch", "RawPitch", "raw_Pitch", "raw_pitch", "Raw_Pitch"]:
            f_raw_pitch = True
        elif sys.argv[i] in ["energy", "Energy"]:
            f_energy = True
        elif sys.argv[i] in ["formants", "Formants"]:
            f_formants = True
        else:
            print("Invalid option:", sys.argv[i])
            sys.exit()

if test == True:
    print("loading test data")
    ms_silver = open("data/test_disfluency/ms_silver", "r")
else:
    print("loading disfluency silver data")
    ms_silver = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/data/silver_wd/ms_silver_word_time_stamps", "r")



max_word_length = 422
num_feats = 0


# Pitch and energy features are computed with Kaldi with a window length of 25ms and a shift of 10 ms
# this means that each value corresponds to a 10 ms frame
# Since window length > shift, the last two frames receive no value
# Therefore, two zero-padded frames are added to match vector length with time stamps as given in MS-State transcripts
if f_pitch == True:
    print("Reading pitch features...")
    pitch_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/F0/pitch_feats", "r")
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

# Raw pitch is almost the same as the first pitch feature; not used for experiments
max_raw_pitch = 400
if f_raw_pitch == True:
    print("Reading raw pitch features...")
    raw_pitch_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/F0/raw_pitch_feats", "r")
    num_feats += 1
    utt_id = ""
    raw_pitch = {}
    for line in raw_pitch_feats:
        line = line.split()
        if line[1] == "[":
            if utt_id != "":
                # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
                raw_pitch[utt_id].append([0.0])
                raw_pitch[utt_id].append([0.0])
            utt_id = line[0]
            raw_pitch[utt_id] = []
        else:
            # 0: NCFF, 1: raw pitch
            p1 = [float(line[1])/max_raw_pitch]
            raw_pitch[utt_id].append(p1)
    # Kaldi feats are computed with sliding window of 25ms, therefore last 2 frames of utt are empty
    raw_pitch[utt_id].append([0.0])
    raw_pitch[utt_id].append([0.0])

# highest total energy in corpus is 25.42658
max_energy = 26
if f_energy == True:
    print("Reading energy features...")
    energy_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy", "r")
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


# For formants, no zero padding is necessary since DeepFormants derives one value for each 10 ms frame
max_f1 = 958.8
max_f2 = 2523.1
max_f3 = 3218.0
max_f4 = 4207.5
if f_formants == True:
    print("Reading formant features...")
    formants_feats = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/formants/formant_feats")
    num_feats += 4
    formants = {}
    for line in formants_feats:
        utt_id, F1, F2, F3, F4 = line.split(",")
        #skip header
        if utt_id != "NAME":
            utt_id = utt_id.replace("switchboard_data_trim", "").strip("./")[:15]
            F4 = F4.strip()
            #fmt1.append(float(F1))
            #fmt2.append(float(F2))
            #fmt3.append(float(F3))
            #fmt4.append(float(F4))
            if utt_id not in formants:
                formants[utt_id] = []
            F1 = float(F1)/max_f1
            F2 = float(F2)/max_f2
            F3 = float(F3)/max_f3
            F4 = float(F4)/max_f4
            formants[utt_id].append([F1, F2, F3, F4])

# The selected prosodic features are combined into one matrix per word which is zero padded if len(word) < max_len_word
print("Gathering prosodic features for each word...")
train_prosody_feats = {}
dev_prosody_feats = {}
test_prosody_feats = {}
count = 1
prev_utt_id = "blub"
utts = []
for line in ms_silver:
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
    elif f_raw_pitch == True:
        w[0:end-start, 0:1] = np.array(raw_pitch[utt_id][start:end], dtype='float32')
    elif f_mean_energy == True:
        w[0:end-start, 0:1] = np.array(mean_energy[utt_id][start:end], dtype='float32')
    elif f_formants == True:
        try:
            w[0:end-start, 0:4] = np.array(formants[utt_id][start:end], dtype='float32')
        # Some formant files are one frame too short
        except:
            w[0:end-start-1, 0:4] = np.array(formants[utt_id][start:end-1], dtype='float32')
    else:
        w[0:end-start, 0:3] = np.array(energy[utt_id][start:end], dtype='float32')
    utt.append(w)
utt = np.array(utt, dtype='float32')
utt_number = int(utt_id[2:6])
if utt_number < 4000:
    train_prosody_feats[utt_id] = utt
elif utt_number > 4499:
    dev_prosody_feats[utt_id] = utt
elif utt_number > 3999 and utt_number < 4200:
    test_prosody_feats[utt_id] = utt

# Write matrices into pickle files
print("Writing pickle files...")
if test == True:
    output1 = open("data/test_disfluency/train_prosody_feats.pkl", "wb")
    output2 = open("data/test_disfluency/dev_prosody_feats.pkl", "wb")
    output3 = open("data/test_disfluency/test_prosody_feats.pkl", "wb")
elif f_pitch == True and f_energy == True and f_formants == True:
    output1 = open("data/disfluency_pitch_energy_formants/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_pitch_energy_formants/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_pitch_energy_formants/test_prosody_feats.pkl", "wb")
elif f_pitch == True and f_energy == True:
    output1 = open("data/disfluency_pitch_energy/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_pitch_energy/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_pitch_energy/test_prosody_feats.pkl", "wb")
elif f_pitch == True:
    output1 = open("data/disfluency_pitch/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_pitch/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_pitch/test_prosody_feats.pkl", "wb")
elif f_energy == True:
    output1 = open("data/disfluency_energy/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_energy/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_energy/test_prosody_feats.pkl", "wb")
elif f_raw_pitch == True:
    output1 = open("data/disfluency_raw_pitch/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_raw_pitch/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_raw_pitch/test_prosody_feats.pkl", "wb")
elif f_mean_energy == True:
    output1 = open("data/disfluency_mean_energy/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_mean_energy/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_mean_energy/test_prosody_feats.pkl", "wb")
elif f_formants == True:
    output1 = open("data/disfluency_formants/train_prosody_feats.pkl", "wb")
    output2 = open("data/disfluency_formants/dev_prosody_feats.pkl", "wb")
    output3 = open("data/disfluency_formants/test_prosody_feats.pkl", "wb")
pkl.dump(train_prosody_feats, output1)
output1.close()
pkl.dump(dev_prosody_feats, output2)
output2.close()
pkl.dump(test_prosody_feats, output3)
output3.close()

