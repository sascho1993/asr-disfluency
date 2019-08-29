"""
Plot results of pitch fine tune on cnn 
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

results = open("results/exp_pitch_fine_tune/dev_results", "r")
results_r2 = open("results/exp_pitch_fine_tune_r2/dev_results", "r")
results_r3 = open("results/exp_pitch_fine_tune_r3/dev_results", "r")


f0 = []
for line in results:
    line = line.split()
    if line[0] == "F1:":
        f0.append(line[1].strip())

f0_r2 = []
for line in results_r2:
    line = line.split()
    if line[0] == "F1:":
        f0_r2.append(line[1].strip())

f0_r3 = []
for line in results_r3:
    line = line.split()
    if line[0] == "F1:":
        f0_r3.append(line[1].strip())

fil = [10,15,20,25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

plt.figure(figsize=[10,5])
plt.plot(fil, np.array(f0,dtype='float32'))
plt.plot(fil, np.array(f0_r2,dtype='float32'))
plt.plot(fil, np.array(f0_r3,dtype='float32'))
#plt.show()
plt.savefig("plots/pitch_fine_tune")
