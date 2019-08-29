"""
Preparation of Kaldi files for forced alignment to get average phone lengths for duration feature.
Words excluded:
  - words from test set
  - non-lexical conversational sounds
  - Reparandum and repair, i.e. everything belonging to a disfluency

The metadata files can be used in Kaldi to generate alignment files.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import math

silver = open("data/silver_wd/reverse_comparison_out", "r")
wav_scp = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/train/wav.scp", 'r')
text = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words/text", 'w')
wav_scp_out = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words/wav.scp", 'w')
utt2spk = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words/utt2spk", 'w')
spk2utt = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words/spk2utt", 'w')
segments = open("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words/segments", 'w')


filler = ["um", "uh", "um-hum", "uh-huh", "huh", "well"]
files = []
prev_file = ""
for line in silver:
    try:
        file_id, token, disfluency, start, end = line.split()
        end = end.strip()
        file_number = file_id[2:6]
        speaker_side = file_id[6:7]
        f = "sw0"+file_number+"-"+speaker_side
        if token not in filler and disfluency == "O" and (int(file_number) < 4000 or int(file_number)> 4200) and end != start:
            text.write("sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end+" "+token+"\n")
            utt2spk.write("sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end+" sw0"+file_number+"-"+speaker_side+"\n")
            st_sec = float(start)/100.0
            end_sec = float(end)/100.0
            segments.write("sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end+" sw0"+file_number+"-"+speaker_side+" "+str(st_sec)+" "+str(end_sec)+'\n')
            if file_number not in files:
                files.append(file_number)
        if int(file_number) < 4000 or int(file_number)> 4200 and end != start:
            # No new line at beginning of file
            if prev_file == "":
                spk2utt.write(f + " " + "sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end)
            # Add utterance to line
            elif prev_file == f:
                spk2utt.write(" sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end)
            # add new line before new speaker
            else:
                spk2utt.write("\n" + f + " " + "sw0"+file_number+"-"+speaker_side+"_"+start+"-"+end)
            prev_file = f
    except:
        pass

for line in wav_scp:
    file_number = line.split()[0][3:7]
    if file_number in files:
        wav_scp_out.write(line)
