import sys
import os

ms_silver_file = open("data/silver_wd/ms_silver_comparison_done", "r")
kaldi_path = "data/kaldi"

ms_silver = {}
for line in ms_silver_file:
    try:
        utt_id, file_id, token, disfluency, start, end = line.split()
        start = int(start)
        end = int(end)
        # new file_id; beginn from time 0
        if file_id not in ms_silver:
            prev_disfl = ""
            prev_end = 0
            ms_silver[file_id] = []
        # if there is silence between last word and this word, append pause_disfluency tag for the duration
        if start - prev_end > 0:
            if prev_disfl == "" or prev_disfl == disfluency:
                p_disfl = disfluency
            else:
                p_disfl = prev_disfl + "-" + disfluency
            ms_silver[file_id].extend([p_disfl]*(start - prev_end))
        # add disfluency tag for word number of frames the word is long
        ms_silver[file_id].extend([disfluency]*(end - start))
        prev_disfl = disfluency
        prev_end = end   
    except:
        pass


for root, dirs, files in os.walk(kaldi_path):
    for k_file in files:
        if "txt" not in k_file:
            kaldi_file = open("{}/{}".format(kaldi_path,k_file), "r")
            out_file = open("{}/{}.txt".format(kaldi_path,k_file), "w")
            prev_utt_id = ""
            for line in kaldi_file:
                utt_id, channel, start, dur, token = line.split()
                file_id = utt_id[0:7]
                start = int(float(start) * 100)
                end = start + int(float(dur) * 100)
                token = token.strip()
                disfluency_list = ms_silver[file_id][start:end]
                disfluency_tags = ["O", "BE_IP", "BE", "IE", "IP", "C", "C_IE", "C_IP"]
                counts = [0,0,0,0,0,0,0,0]
                for d in disfluency_list:
                    if len(d.split("-")) == 1:
                        if d == "O":
                            counts[0] += 1
                        elif d == "BE_IP":
                            counts[1] += 1
                        elif d == "BE":
                            counts[2] += 1
                        elif d == "IE":
                            counts[3] += 1
                        elif d == "IP":
                            counts[4] += 1
                        elif d == "C":
                            counts[5] += 1
                        elif d == "C_IE":
                            counts[6] += 1
                        elif d == "C_IP":
                            counts[7] += 1
                    else:
                        for d_s in [d.split("-")[0], d.split("-")[1]]:
                            if d == "O":
                                counts[0] += 0.5
                            elif d == "BE_IP":
                                counts[1] += 0.5
                            elif d == "BE":
                                counts[2] += 0.5
                            elif d == "IE":
                                counts[3] += 0.5
                            elif d == "IP":
                                counts[4] += 0.5
                            elif d == "C":
                                counts[5] += 0.5
                            elif d == "C_IE":
                                counts[6] += 0.5
                            elif d == "C_IP":
                                counts[7] += 0.5
                disfluency = disfluency_tags[index(max(counts))]
                if prev_utt_id != "" and prev_utt_id != utt_id:
                    #out_file.write('\n')
                    print '\n'
                #out_file.write(utt_id + '\t' + token + '\t' + disfluency + '\t' + str(start) + '\t' + str(end) + '\n')
                prev_utt_id = utt_id
                print utt_id + '\t' + token + '\t' + disfluency + '\t' + str(start) + '\t' + str(end)
            
