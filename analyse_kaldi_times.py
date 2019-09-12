silver = open("data/silver_wd/ms_silver_word_time_stamps", "r")
kaldi = open("data/kaldi/score_17_1.0", "r")

s = {}
for line in silver:
    try:
        utt_id, file_id, token, dislfuency, start, end = line.split()
    except:
        s[utt_id] = int(end)

k = {}
for line in kaldi:
    try:
        utt_id, file_id, token, dislfuency, start, end = line.split()
    except:
        k[utt_id] = int(end)

for utt in k:
    if k[utt] > s[utt]:
        print utt, k[utt], s[utt]