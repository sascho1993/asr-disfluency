"""
Plot the F-score of a model on all kaldi outputs
x-axis: LMWT
y-axis: F-score
three curves: one per word insertion penalty

Usage:
  python plot_kaldi_test.py results/kaldi_test/{experiment}
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

x = [5,6,7,8,9,10,11,12,13,14,15,16,17]
wips = ["0.0", "0.5", "1.0"]

decode_path = "/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/exp/chain/tdnn7q_sp/decode_disfluency_silver_uttids_sw1_tg"

z_z = []
z_five = []
one_z = []
wer_z_z = []
wer_z_five = []
wer_one_z = []
kaldi_test = sys.argv[1].strip("/")
experiment = kaldi_test.split("/")[-1]
for LMWT in x:
    for wip in wips:
        f = open("{0}/{1}_{2}/dev_{1}_{2}_results".format(kaldi_test, LMWT, wip), "r")
        f_scores = []
        for line in f:
            if line.split()[0] == "F1:":
                f_scores.append(line.split()[1].strip())
        f.close()
        mean_f = np.mean(np.array(f_scores, dtype='float32'))
        f = open("{}/wer_{}_{}".format(decode_path, LMWT, wip))
        for line in f:
            if line.split()[0] == "%WER":
                wer = line.split()[1]
        f.close()
        if wip == "0.0":
            z_z.append(mean_f)
            wer_z_z.append(wer)
        elif wip == "0.5":
            z_five.append(mean_f)
            wer_z_five.append(wer)
        else:
            one_z.append(mean_f)
            wer_one_z.append(wer)
            

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('LMWT')
ax1.set_ylabel('F-score', color=color)
ax1.plot(x, np.array(z_z,dtype='float32'), color=color)
ax1.plot(x, np.array(z_five,dtype='float32'), color=color, linestyle='--')
ax1.plot(x, np.array(one_z,dtype='float32'), color=color, linestyle=':')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('WER', color=color)  # we already handled the x-label with ax1
ax2.plot(x, np.array(wer_z_z,dtype='float32'), color=color)
ax2.plot(x, np.array(wer_z_five,dtype='float32'), color=color, linestyle='--')
ax2.plot(x, np.array(wer_one_z,dtype='float32'), color=color, linestyle=':')
ax2.tick_params(axis='y', labelcolor=color)


fig.tight_layout()  # otherwise the right y-label is slightly clipped
#plt.show()
plt.savefig("plots/kaldi_test_{}.pdf".format(experiment))

"""
plt.figure(figsize=[10,5])
plt.plot(x, np.array(z_z,dtype='float32'), label='WIP = 0.0')
plt.plot(x, np.array(z_five,dtype='float32'), label='WIP = 0.5')
plt.plot(x, np.array(one_z,dtype='float32'), label='WIP = 1.0')
plt.legend()
plt.show()
plt.savefig("plots/kaldi_test_exp_silver_dev")"""
