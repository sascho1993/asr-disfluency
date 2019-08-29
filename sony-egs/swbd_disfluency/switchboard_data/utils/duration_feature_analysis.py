import sys
import numpy as np
import matplotlib.pyplot as plt
import math

phones_file = open("audio/duration_feats/phones.txt", 'r')
ali_file = open("audio/duration_feats/kaldi_ali_phones_only_fluent", 'r')
lexicon_file = open("audio/duration_feats/lexicon.txt", 'r')
silver = open("data/silver_wd/ms_silver_word_time_stamps", "r")
all_ms = open("audio/duration_feats/words", "r")
#https://semanticsimilarity.wordpress.com/function-word-lists/
function_words_file = open("audio/helpers/function_words", "r")

no_phones = ['#0','#1','#2','#3','#4','#5','#6','#7','#8','#9','#10','<eps>']

# dictionary to map phone ids to phone names - id : phone_name
phone_ids = {}
phones = []
for line in phones_file:
    phone, phone_id = line.split()
    phone_id = phone_id.strip()
    phone = phone.replace("_B", "").replace("_E", "").replace("_I", "").replace("_S", "")
    phone_ids[phone_id] = phone
    if phone not in phones and phone not in no_phones:
        phones.append(phone)

# dictionary to store each phone with durations of alignment file - phone_name : [dur1, dur2, dur3, ...]
phone_durs = {}
for p in phones:
    phone_durs[p] = []
for line in ali_file:
    line = line.split(";")
    for entry in line:
        entry = entry.strip().split()
        if len(entry) == 3:
            phone_id = entry[1]
            dur = entry[2]
        else:
            phone_id = entry[0]
            dur = int(entry[1])
        phone = phone_ids[phone_id]
        phone_durs[phone].append(dur)

# dictionary to store each phone with its mean duration and std - phone_name : [mean_dur, std]
phone_stats = {}
for key in phone_durs:
    number_occ = len(phone_durs[key])
    mean_dur = np.mean(np.array(phone_durs[key], dtype='float64'))
    p_std = np.std(np.array(phone_durs[key], dtype='float64'))
    phone_stats[key] = [mean_dur, p_std]

# lexicon - word - [phone1, phone2, phone3, ...]
lexicon = {}
for line in lexicon_file:
    line = line.split()
    word = line[0]
    pron = line[1:]
    if word not in lexicon:
        lexicon[word] = pron
    else:
        lexicon[word].extend(pron)

# lexicon containing word durations of the whole MS-State corpus
ms_word_dur = {}
for line in all_ms:
    try:
        utt_id, token, start, end = line.split()
        start = int(start)
        end = int(end)
        dur = end-start
        if token not in ms_word_dur:
            ms_word_dur[token] = [dur]
        else:
            ms_word_dur[token].append(dur)
    except:
        pass

# Get mean and std values for words that occur 15+ times in MS-state corpus
ms_word_stats = {}
for key in ms_word_dur:
    if len(ms_word_dur[key]) > 15:
        ms_mean = np.mean(np.array(ms_word_dur[key]))
        ms_std = np.std(np.array(ms_word_dur[key]))
        ms_word_stats[key] = [ms_mean, ms_std]



lexicon_mean = {}
lexicon_std = {}
for key in lexicon:
    word_mean = 0
    word_std = 0
    for phone in lexicon[key]:
        phone_mean = phone_stats[phone][0]
        word_mean += phone_mean
        phone_std = phone_stats[phone][1]
        word_std += phone_std
    lexicon_mean[key] = word_mean
    lexicon_std[key] = word_std

function_words = []
for line in function_words_file:
    function_words.append(line.strip())


prev_end = 0
dur_feats_phones_rm = []
dur_feats_phones_rr = []
dur_feats_phones_fluent = []
dur_feats_words_rm = []
dur_feats_words_rr = []
dur_feats_words_fluent = []
dur_feats_same_rm = []
dur_feats_same_rr = []
dur_feats_same_fluent = []

dur_feats_phones_rm_function = []
dur_feats_phones_rr_function = []
dur_feats_phones_fluent_function = []
dur_feats_words_rm_function = []
dur_feats_words_rr_function = []
dur_feats_words_fluent_function = []
dur_feats_same_rm_function = []
dur_feats_same_rr_function = []
dur_feats_same_fluent_function = []
pause_rm = []
pause_rr = []
pause_fluent = []
for line in silver:
    try:
        utt_id, file_id, token, disfluency, start, end = line.split()
        start = float(start)
        end = float(end)
        pause = start - prev_end
        pause_ln = min(1, math.log((pause/100) + 1))
        if disfluency == "C" and pause > 0 and pause < 200:
            pause_rr.append(pause)
        elif disfluency == "O" and pause > 0 and pause < 200:
            pause_fluent.append(pause)
        elif pause > 0 and pause < 200:
            pause_rm.append(pause)
        dur = end-start
        mean_dur_phones = lexicon_mean[token]
        dur_feat_phone = (min(5, dur / mean_dur_phones)-1)/4
        #dur_feats_phones.append(dur_feat_phone)
        if token in ms_word_stats:
            dur_feat_word = (min(5, dur / ms_word_stats[token][0])-1)/4
        else:
            dur_feat_word = dur_feat_phone
        #dur_feats_words.append(dur_feat_word)
        if disfluency == "C" and dur_feat_phone!=dur_feat_word and token in function_words:
            dur_feats_phones_rr_function.append(dur_feat_phone)
            dur_feats_words_rr_function.append(dur_feat_word)
        elif disfluency == "C" and token in function_words:
            dur_feats_same_rr_function.append(dur_feat_phone)
        elif disfluency == "O" and dur_feat_phone!=dur_feat_word and token in function_words:
            dur_feats_phones_fluent_function.append(dur_feat_phone)
            dur_feats_words_fluent_function.append(dur_feat_word)
        elif disfluency == "O" and token in function_words:
            dur_feats_same_fluent_function.append(dur_feat_phone)
        elif dur_feat_phone!=dur_feat_word and token in function_words:
            dur_feats_phones_rm_function.append(dur_feat_phone)
            dur_feats_words_rm_function.append(dur_feat_word)
        elif token in function_words:
            dur_feats_same_rm_function.append(dur_feat_phone)
        # content words
        elif disfluency == "C" and dur_feat_phone!=dur_feat_word:
            dur_feats_phones_rr.append(dur_feat_phone)
            dur_feats_words_rr.append(dur_feat_word)
        elif disfluency == "C":
            dur_feats_same_rr.append(dur_feat_phone)
        elif disfluency == "O" and dur_feat_phone!=dur_feat_word:
            dur_feats_phones_fluent.append(dur_feat_phone)
            dur_feats_words_fluent.append(dur_feat_word)
        elif disfluency == "O":
            dur_feats_same_fluent.append(dur_feat_phone)
        elif dur_feat_phone!=dur_feat_word:
            dur_feats_phones_rm.append(dur_feat_phone)
            dur_feats_words_rm.append(dur_feat_word)
        else:
            dur_feats_same_rm.append(dur_feat_phone)
        #print utt_id + '\t' + token + '\t' + disfluency + '\t' + str(dur_feat_phone) + '\t' + str(dur_feat_word) + '\t' + str(pause_ln)
        prev_end = end
    except:
        #print ""
        prev_end = 0

print "content words:"
print "frequent rm:", len(dur_feats_phones_rm)
print "frequent rr:", len(dur_feats_phones_rr)
print "frequent fluent:", len(dur_feats_phones_fluent)
print "infrequent rm:", len(dur_feats_same_rm)
print "infrequent rr:", len(dur_feats_same_rr)
print "infrequent fluent:", len(dur_feats_same_fluent)

print "function words:"
print "frequent rm:", len(dur_feats_phones_rm_function)
print "frequent rr:", len(dur_feats_phones_rr_function)
print "frequent fluent:", len(dur_feats_phones_fluent_function)
print "infrequent rm:", len(dur_feats_same_rm_function)
print "infrequent rr:", len(dur_feats_same_rr_function)
print "infrequent fluent:", len(dur_feats_same_fluent_function)

fig, axs = plt.subplots(6, figsize=(20,12))
axs[0].title.set_text("Content words: Reparandum")
axs[0].hist(dur_feats_phones_rm, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[0].hist(dur_feats_words_rm, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[0].hist(dur_feats_same_rm, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[0].set_ylim([0,900])
axs[0].legend()
axs[1].title.set_text("Content words: Repair")
axs[1].hist(dur_feats_phones_rr, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[1].hist(dur_feats_words_rr, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[1].hist(dur_feats_same_rr, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[1].set_ylim([0,1400])
axs[1].legend()
axs[2].title.set_text("Content words: Fluent words")
axs[2].hist(dur_feats_phones_fluent, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[2].hist(dur_feats_words_fluent, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[2].hist(dur_feats_same_fluent, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[2].legend()
axs[3].title.set_text("Function words: Reparandum")
axs[3].hist(dur_feats_phones_rm_function, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[3].hist(dur_feats_words_rm_function, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[3].hist(dur_feats_same_rm_function, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[3].legend()
axs[4].title.set_text("Function words: Repair")
axs[4].hist(dur_feats_phones_rr_function, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[4].hist(dur_feats_words_rr_function, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[4].hist(dur_feats_same_rr_function, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[4].legend()
axs[5].title.set_text("Function words: Fluent words")
axs[5].hist(dur_feats_phones_fluent_function, alpha=0.5, label="phones", bins=300, histtype='stepfilled')
axs[5].hist(dur_feats_words_fluent_function, alpha=0.5, label="words", bins=300, histtype='stepfilled')
axs[5].hist(dur_feats_same_fluent_function, alpha=0.5, label="same", bins=300, histtype='stepfilled')
axs[5].legend()

plt.subplots_adjust(hspace=0.5)
#plt.show()
plt.savefig("audio/duration_feats/word_durations_all_swbd")

"""
fig, axs = plt.subplots(3, sharex=True, sharey=True)
axs[0].hist(np.array(pause_rm), bins = 300, label = 'Reparandum')
axs[0].legend()
axs[1].hist((np.array(pause_rr)), bins = 300, label = 'Repair', color="g")
axs[1].legend()
axs[2].hist((np.array(pause_fluent)), bins = 300, label = 'Fluent', color="r")
#plt.hist(np.array(pause_rm), bins = 300, label = 'Reparandum', alpha=0.5)
#plt.hist((np.array(pause_rr)), bins = 300, label = 'Repair', alpha=0.5)
#plt.hist((np.array(pause_fluent)), bins = 300, label = 'Fluent', alpha=0.5)
axs[2].legend()
plt.subplots_adjust(hspace=None)
plt.show()
"""
