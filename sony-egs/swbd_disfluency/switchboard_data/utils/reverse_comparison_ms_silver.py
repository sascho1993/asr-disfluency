"""
This script is used after compare_silver_ms.py
It is necessary for cases like:
*just
*a
*second
just
one
moment
, where words marked by * are only in the MS-state transcripts and not in the silver ones.
compare_silver_ms.py is greedy and will choose the first 'just'.
This script iterates through the output of the first comparison in reversed order and chooses the word with the correct time stamps.
"""

import sys
import ast
import re

comp = open(sys.argv[1], "r")
ms = open(sys.argv[2], "r")


ms_corpus = {}
for line in ms:
    file_id, word = line.split()
    file_key = file_id[0:2] + file_id[3:7] + file_id[8:9]
    start = file_id[10:16]
    end = file_id[17:]
    if file_key not in ms_corpus:
        ms_corpus[file_key] = [[], [], []]
    ms_corpus[file_key][0].append(word)
    ms_corpus[file_key][1].append(start)
    ms_corpus[file_key][2].append(end)

comparison = {}
for line in comp:
    try:
        key_ms, key_silver, ms_word, silver_word, silver_tag, start, end = line.split('\t')
        key_silver = key_silver.strip()
        if key_ms not in comparison:
            comparison[key_ms] = [[], [], [], [], []]
        key = comparison[key_ms]
        key[0].append(ms_word.strip())
        key[1].append(silver_word.strip())
        key[2].append(silver_tag.strip())
        key[3].append(start.strip())
        key[4].append(end.strip())
    except:
        key = comparison[key_ms]
        key[0].append("XXXXXX")
        key[1].append("XXXXXX")
        key[2].append(None)
        key[3].append(None)
        key[4].append(None)

output = {}
for key in sorted(comparison.keys()):
    # reverse order of words etc.
    ms_words = ms_corpus[key][0][::-1]
    ms_start_times = ms_corpus[key][1][::-1]
    ms_end_times = ms_corpus[key][2][::-1]
    comp_ms_words = comparison[key][0][::-1]
    comp_silver_words = comparison[key][1][::-1]
    comp_disfluency_tags = comparison[key][2][::-1]
    comp_start_times = comparison[key][3][::-1]
    comp_end_times = comparison[key][4][::-1]
    sentence_count = comp_ms_words.count('XXXXXX')
    ms_count = 0
    comp_count = 0
    if key not in output:
        output[key] = []
    for i in range(len(ms_words) + sentence_count):
        ms_word = ms_words[i + ms_count].strip()
        try:
            comp_ms_word = comp_ms_words[i + comp_count]
            comp_start_time = comp_start_times[i + comp_count]
            comp_end_time = comp_end_times[i + comp_count]
            comp_disfluency_tag = comp_disfluency_tags[i + comp_count]
            comp_silver_word = comp_silver_words[i + comp_count]
        except:
            continue
        ms_start_time = ms_start_times[i + ms_count]
        ms_end_time = ms_end_times[i + ms_count]
        if comp_ms_word == 'XXXXXX':
            if i + comp_count == len(comp_ms_words) - 1:
                break
            else:
                ms_count -= 1
                output[key].append('')
        elif ms_word == comp_ms_word and ms_start_time == comp_start_time and ms_end_time == comp_end_time:
            # Decide whether to use MS-State or silver word
            # General rule: Use the transcription that is closer to ASR output (i.e. only lexemes, acronym regulations)
            # except if MS-State is a words fragment

            # e.g. members'
            if comp_silver_word.strip("'") == ms_word:
                output[key].append(key + '\t' + comp_silver_word + '\t' + comp_disfluency_tag + '\t' + ms_start_time + '\t' + ms_end_time)
            # e.g. o'clock, word fragments, a._c._d._c., a._c._d._c.'s
            elif ms_word == "gonna" or ms_word == "wanna" \
                    or comp_silver_word == ms_word.replace("'", "") \
                    or ms_word[-1] == "-" \
                    or re.match("([a-z]\._)*[a-z]\.", ms_word) \
                    or re.match("([a-z]\._)*[a-z]\.'s", ms_word) \
                    or comp_silver_word == 'pw65':
                output[key].append(key + '\t' + ms_word + '\t' + comp_disfluency_tag + '\t' + ms_start_time + '\t' + ms_end_time)
            else:
                output[key].append(key + '\t' + comp_silver_word + '\t' + comp_disfluency_tag + '\t' + ms_start_time + '\t' + ms_end_time)
        # sw2260B is an exception, the only ambiguous time stamp is correct after the first comparison
        elif ms_word == comp_ms_word and int(ms_start_time) > int(comp_start_time) and key != "sw2260B":
            output[key].append(key + '\t' + ms_word + '\t' + comp_disfluency_tag + '\t' + ms_start_time + '\t' + ms_end_time)
        else:
            comp_count -= 1

# Re-reverse to get output in correct order
for key in sorted(output.keys()):
        for line in reversed(output[key]):
            print line



 
