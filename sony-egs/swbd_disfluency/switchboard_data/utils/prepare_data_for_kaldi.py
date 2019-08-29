"""
Generate Kaldi files for silver data:
  - wav.scp
  - text
  - utt2spk
  - segments
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import math

kaldi_dir = "/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_no_fragments/"
train = "data/train/"
disfluency_dir = "data/disfluency_silver_uttids/"

silver = open("data/silver_wd/ms_silver_for_kaldi", "r")

wav_scp = open(kaldi_dir+train+"wav.scp", 'r')
text = open(kaldi_dir+disfluency_dir+"text", 'w')
wav_scp_out = open(kaldi_dir+disfluency_dir+"wav.scp", 'w')
utt2spk = open(kaldi_dir+disfluency_dir+"utt2spk", 'w')
segments = open(kaldi_dir+disfluency_dir+"segments", 'w')

discard_utts = []
for line in discarded:
    if line.strip() != "":
        discard_utts.append(line.strip())


utts = []
sentence = ""
new_utt = True
speaker = {}
files = []
prev_file_id = ""
for line in silver:
    try:
        utt_id, file_id, token, disfluency, start, end = line.split()
        if prev_file_id != file_id:
            file_id_count = 1
        prev_file_id = file_id
        end = end.strip()
        if new_utt == True:
            utt_start = start
            new_utt = False
        if token.strip("-") == token:
            sentence += token + " "
        if file_id not in files:
            files.append(file_id[2:6])
    except:
        if utt_start != end:
            new_utt = True
            if utt_id[6] == 'A':
                utt_id = utt_id + "-a-" + utt_start + "-" + end
            elif utt_id[6] == 'B':
                utt_id = utt_id + "-b-" + utt_start + "-" + end
            else:
                print("speaker side must be A or B")
            utts.append([utt_id, sentence.strip()])
            utt2spk.write(utt_id + " " + file_id + '\n')
            text.write(utt_id + " " + sentence + '\n')
            segments.write(utt_id + " " + file_id + " " + str(float(utt_start)/100) + " " + str(float(end)/100) + '\n')
            sentence = ""


for line in wav_scp:
    file_number = line.split()[0][3:7]
    if file_number in files:
        #print line
        line = line.replace("spielwiese3/deschops", "spielwiese4/students/deschops")
        line = line.replace("sw0", "sw")
        line = line.replace("data/sw", "data/sw0")
        line = line.replace("-A", "A")
        line = line.replace("-B", "B")
        wav_scp_out.write(line)

