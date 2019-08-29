from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile

file_name = sys.argv[1]

formant_file = open(file_name + "_formants", "r")

fmt1 = []
fmt2 = []
fmt3 = []
fmt4 = []
Fmt1 = []
Fmt2 = []
Fmt3 = []
Fmt4 = []
max_f1 = 958.8
max_f2 = 2523.1
max_f3 = 3218.0
max_f4 = 4207.5
for line in formant_file:
    utt_id, F1, F2, F3, F4 = line.split(",")
    utt_id = utt_id.strip("./")[:15]
    F4 = F4.strip()
    fmt1.append(float(F1))
    fmt2.append(float(F2))
    fmt3.append(float(F3))
    fmt4.append(float(F4))
    F1 = float(F1)/max_f1
    F2 = float(F2)/max_f2
    F3 = float(F3)/max_f3
    F4 = float(F4)/max_f4
    Fmt1.append(float(F1))
    Fmt2.append(float(F2))
    Fmt3.append(float(F3))
    Fmt4.append(float(F4))



sample_rate, samples = wavfile.read(file_name+"_16k.wav")
sample_scale = [i/sample_rate for i in range(1,len(samples)+1)]
sample_scale_feats = [i/100 for i in range(1, len(fmt1)+1)]

frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)


fig, axs = plt.subplots(10, sharex=True)
#fig, axs = plt.subplots(8, sharex=True)

#plt.pcolormesh(times, frequencies, spectrogram)

axs[0].plot(sample_scale, samples)
axs[1].specgram(samples, Fs=sample_rate, NFFT=512)
axs[1].set_yticks(range(0,5000,1000))
#axs[1].imshow(spectrogram)
#plt.axis(ymax=4000)

axs[2].plot(sample_scale_feats, fmt1)
axs[3].plot(sample_scale_feats, fmt2)
axs[4].plot(sample_scale_feats, fmt3)
axs[5].plot(sample_scale_feats, fmt4)
axs[6].plot(sample_scale_feats, Fmt1)
axs[7].plot(sample_scale_feats, Fmt2)
axs[8].plot(sample_scale_feats, Fmt3)
axs[9].plot(sample_scale_feats, Fmt4)


plt.subplots_adjust(hspace=0)

plt.show()
