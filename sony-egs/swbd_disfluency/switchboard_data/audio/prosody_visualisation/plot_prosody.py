from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile

file_name = sys.argv[1]

raw_pitch_f = open(file_name + "_raw_pitch", "r")
pitch_f = open(file_name + "_pitch", "r")
energy_f = open(file_name + "_energy", "r")

raw_pitch = []
NCFF = []
for line in raw_pitch_f:
    line = line.split()
    if line[1] != "[":
        NCFF.append(line[0])
        raw_pitch.append(line[1])
raw_pitch = np.array(raw_pitch)
NCFF = np.array(NCFF)

pov = []
norm_pitch = []
delta = []
for line in pitch_f:
    line = line.split()
    if line[1] != "[":
        pov.append(line[0])
        norm_pitch.append(line[1])
        delta.append(line[2])
pov = np.array(pov)
norm_pitch = np.array(norm_pitch)
delta = np.array(delta)

max_energy = 26
e_low = []
e_high = []
e_total = []
for line in energy_f:
    line = line.split()
    if line[1] != "[":
        #e_total.append(float(line[0])/max_energy)
        e_total.append(float(line[0]))
        e_low.append(np.log(np.sum(np.exp(np.array(line[1:21], dtype='float32'))))/float(line[0]))
        e_high.append(np.log(np.sum(np.exp(np.array(line[21:41], dtype='float32'))))/float(line[0]))
e_low = np.array(e_low)
e_high = np.array(e_high)
e_total = np.array(e_total)

sample_rate, samples = wavfile.read(file_name+"_16k.wav")
sample_scale = [i/sample_rate for i in range(1,len(samples)+1)]
sample_scale_feats = [i/100 for i in range(1, raw_pitch.shape[0]+1)]

frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)


fig, axs = plt.subplots(10, sharex=True)
#fig, axs = plt.subplots(8, sharex=True)

#plt.pcolormesh(times, frequencies, spectrogram)

axs[0].plot(sample_scale, samples)
axs[1].specgram(samples, Fs=sample_rate, NFFT=512)
axs[1].set_yticks(range(0,5000,1000))
#axs[1].imshow(spectrogram)
#plt.axis(ymax=4000)

axs[2].plot(sample_scale_feats, raw_pitch)
plt.ylabel('raw pitch')
axs[3].plot(sample_scale_feats, NCFF)
plt.ylabel('NCFF')

axs[4].plot(sample_scale_feats, pov)
plt.ylabel('pov')
axs[5].plot(sample_scale_feats, norm_pitch)
plt.ylabel('norm_pitch')
axs[6].plot(sample_scale_feats, delta)
plt.ylabel('delta')

axs[7].plot(sample_scale_feats, e_high)
plt.ylabel('e_high')
axs[8].plot(sample_scale_feats, e_low)
plt.ylabel('e_low')
axs[9].plot(sample_scale_feats, e_total)
plt.ylabel('e_total')
#axs[7].plot(sample_scale_feats, e_total)
#plt.ylabel('e_total')

plt.subplots_adjust(hspace=0)

plt.show()
