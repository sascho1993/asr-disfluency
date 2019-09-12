import numpy as np
import sys

max_f1 = 958.8
max_f2 = 2523.1
max_f3 = 3218.0
max_f4 = 4207.5

formants_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/formants/formant_feats")
formants = {}
for line in formants_feats:
  utt_id, F1, F2, F3, F4 = line.split(",")
  if utt_id != "NAME":
    utt_id = utt_id.replace("switchboard_data_trim", "").strip("./")[:15]
    F4 = F4.strip()
    F1 = float(F1)/max_f1
    F2 = float(F2)/max_f2
    F3 = float(F3)/max_f3
    F4 = float(F4)/max_f4
    print utt_id, F1, F2, F3, F4
