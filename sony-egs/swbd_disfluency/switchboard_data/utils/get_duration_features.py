"""
This script generates duration features in 8 steps:
  - phone id dictionary - phone id : phone name
  - read kaldi alignments and store phone durations in dictionary - phone name : [dur1, dur2, dur3, ...]
  - Get mean duration and std for each phone - phone name : [mean_dur, std]
  - Store lexicon with all pronunciation variants in dictionary
  - dictionary to store whole word durations from MS-State corpus - word : [dur1, dur2, dur3, ...]
  - Get mean duration and std for each word - word : [mean_dur, std]
      -> if word freq < 15, phone means are used
  - Get mean duration of words in lexicon based on mean phone durations
  - Write new data file with added duration features: word_dur_word, word_dur_phone, pause_dur;  where
      - word_dur_phone ~ dur(word) / mean_dur(phone1, phone2,...)  
      - word_dur_word ~ dur(word) / mean_dur(word) if frequ(word) > 15, else: word_dur_phone
      - pause_dur ~ ln(pause length after previous word)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import math

phones_file = open("audio/duration_feats/phones.txt", 'r')
ali_file = open(sys.argv[1], 'r')
lexicon_file = open("audio/duration_feats/lexicon.txt", 'r')
if len(sys.argv) == 0:
    silver = open("data/silver_wd/ms_silver_word_time_stamps", "r")
else:
    silver = open(sys.argv[1], "r")
all_ms = open("audio/duration_feats/words", "r")

no_phones = ['#0','#1','#2','#3','#4','#5','#6','#7','#8','#9','#10','<eps>', 'lau', 'nsn']

# dictionary to map phone ids to phone names - id : phone_name
phone_ids = {}
phones = []
for line in phones_file:
    phone, phone_id = line.split()
    phone_id = phone_id.strip()
    # Merge triphones into one phoneme category
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
    try:
        number_occ = len(phone_durs[key])
        mean_dur = np.mean(np.array(phone_durs[key], dtype='float64'))
        p_std = np.std(np.array(phone_durs[key], dtype='float64'))
        phone_stats[key] = [mean_dur, p_std]
    except:
        pass
# laughter
phone_stats['lau'] = [0,0]
# non-speech noise
phone_stats['nsn'] = [0,0]


# lexicon: word - [phone1, phone2, phone3, ...]
lexicon = {}
for line in lexicon_file:
    line = line.split()
    word = line[0]
    pron = line[1:]
    if word not in lexicon:
        lexicon[word] = pron
    else:
        lexicon[word].extend(pron)
    # For Kaldi output, acronyms are spelled c i a instead of c._i._a.
    if word.strip(".") != word and "_" not in word:
        letter = word.strip(".")
        if letter not in lexicon:
            lexicon[letter] = pron
        else:
            lexicon[letter].extend(pron)
        # e.g. c's; not sure where they come from since 's was split from all words in lexicon before ASR training
        word_apos = letter + "'s"
        pron_apos = pron[:]
        if pron_apos[-1] == 's':
            pron_apos.append("ih")
        pron_apos.append("z")
        if word_apos not in lexicon:
            lexicon[word_apos] = pron_apos
        else:
            lexicon[word_apos].extend(pron_apos)

# dictionary containing word durations of the whole MS-State corpus
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


# Dictionaries with mean and std of word based on mean length of phoneme
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

# print dataset with additional durational features word_dur_phone, word_dur_word, pause
prev_end = 0
dur_feats_phones = []
dur_feats_words = []
for line in silver:
    try:
        utt_id, file_id, token, disfluency, start, end = line.split()
        start = float(start)
        end = float(end)
        pause = start - prev_end
        pause_ln = min(1, math.log((pause/100) + 1))
        dur = end-start
        mean_dur_phones = lexicon_mean[token]
        dur_feat_phone = (min(5, dur / mean_dur_phones)-1)/4
        dur_feats_phones.append(dur_feat_phone)
        if token in ms_word_stats:
            dur_feat_word = (min(5, dur / ms_word_stats[token][0])-1)/4
        else:
            dur_feat_word = dur_feat_phone
        dur_feats_words.append(dur_feat_word)
        print utt_id + '\t' + token + '\t' + disfluency + '\t' + str(dur_feat_phone) + '\t' + str(dur_feat_word) + '\t' + str(pause_ln)
        prev_end = end
    except:
        print ""
        prev_end = 0


"""
fig, axs = plt.subplots(2)
axs[0].hist(np.array(dur_feats_phones), bins = 300)
axs[1].hist((np.array(dur_feats_words)), bins = 300)
plt.show()
"""
