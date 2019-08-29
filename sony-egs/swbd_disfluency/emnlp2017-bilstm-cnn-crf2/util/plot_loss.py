"""
Plot the train and dev loss from a log file.
Produces as many plots as experiments are contained in the log file

Usage:
  python plot_loss.py logs/{log_file}
"""

import sys
import matplotlib.pyplot as plt
import numpy as np

log_file = open(sys.argv[1], 'r')

train_loss = []
dev_loss = []
count = 0
for line in log_file:
    line = line.split()
    line.extend(['padding', 'padding'])
    #print(line)
    if line[0] == '---' and line[2] == '---':
        train = []
        dev = []
    elif line[0] == 'train' and line[1] == 'loss:':
        train.append(line[2])
    elif line[0] == 'dev' and line[1] == 'loss:':
        dev.append(line[2])
    elif line[0] == '!!!' and line[1] == 'Early' and line[2] == 'stopping,':
        train_loss.append(train)
        dev_loss.append(dev)
        count += 1


fig, axs = plt.subplots(count, sharex=True)

for i in range(count):
    axs[i].plot(np.array(train_loss[i], dtype='float32'))
    axs[i].plot(np.array(dev_loss[i], dtype='float32'))

plt.show()
