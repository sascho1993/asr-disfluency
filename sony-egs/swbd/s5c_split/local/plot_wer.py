import numpy as np
import matplotlib.pyplot as plt
import sys

x = [5,6,7,8,9,10,11,12,13,14,15,16,17]
insertion_penalties = ["0.0", "0.5", "1.0"]

decode_path = "/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_no_fragments/exp/chain/tdnn7q_sp/decode_disfluency_silver_uttids_sw1_tg"

fig, axs = plt.subplots(2,2, sharex=True)
for insertion_penalty in insertion_penalties:
    wer = []
    insertions = []
    deletions = []
    substitutions = []
    for LMWT in x:
        f = open("{0}/wer_{1}_{2}".format(decode_path, LMWT, insertion_penalty), "r")
        for line in f:
            if line.split()[0] == "%WER":
                wer.append(line.split()[1])
                insertions.append(line.split()[6])
                deletions.append(line.split()[8])
                substitutions.append(line.split()[10])
    axs[0,0].plot(x, np.array(wer, dtype='float32'))
    axs[0,0].set(ylabel="WER in %")
    axs[0,1].plot(x, np.array(insertions,dtype='int32')/1000, label="WIP: {}".format(insertion_penalty))
    axs[0,1].set(ylabel="Word insertions in k")
    axs[1,0].plot(x, np.array(deletions,dtype='int32')/1000)
    axs[1,0].set(xlabel="LMWT",ylabel="Word deletions in k")
    axs[1,1].plot(x, np.array(substitutions,dtype='int32')/1000)
    axs[1,1].set(xlabel="LMWT",ylabel="Word substitutions in k")
    
    
axs[0,1].legend(prop={'size': 12})
plt.subplots_adjust(wspace=0.3)
#plt.show()

plt.savefig("/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/emnlp2017-bilstm-cnn-crf2/plots/ASR_output")

