import numpy as np
import sys

max_energy = 26
energy_feats = open("/Users/Sarah/sony_files/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy", "r")

utt_id = ""
energy = {}
for l in energy_feats:
  line = l.split()
  if line[1] == "[":
    utt_id = line[0]
    print l.strip()
  else:
    e = float(line[0])
    total = e/max_energy
    fbank_low = np.log(np.sum(np.exp(np.array(line[1:21], dtype='float32'))))/e
    fbank_high = np.log(np.sum(np.exp(np.array(line[21:41], dtype='float32'))))/e
  if len(line) == 42:
    print str(total),  str(fbank_low),  str(fbank_high), ']'
  elif len(line) == 41:
    print str(total),  str(fbank_low), str(fbank_high)
