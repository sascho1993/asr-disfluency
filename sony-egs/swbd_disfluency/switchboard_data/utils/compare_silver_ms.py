"""
The Ms-State and silver transcripts differ in the following aspects:
- Ms-State contains narrow transcriptions (e.g. gonna instead of going to, bamorghini instead of lamborghini)
- Ms-State does not split apostrophes: she's instead of she 's
- Silver transcripts only contain speech that was originally in the Treebank, Ms-State also contains speech directed at other people than the second caller
- In some files, speaker A and B are swapped (see ab_swapped)

In this script the two transcripts are mapped. Everything that is only in one transcript is omitted. Disfluency tags are added from silver transcripts and time stamps from Ms-State transcripts.
"""

import sys
import ast
import re

silver = sys.stdin.readlines()
ms = open(sys.argv[1], "r")
ab_swapped = open(sys.argv[2], "r")

# files where A and B are opposite in MS-State transcripts and silver transcripts
swap = []
for line in ab_swapped:
    swap.append(line.strip())

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

c = 0
silver_corpus = {}
for line in silver:
    # skip header
    if c == 0:
        c += 1
        continue
    line = line.split('\t')
    ms_sentence = ast.literal_eval(line[5].strip('"'))
    # -- and // are non-tokens without corresponding tags in the other lists, they can be skipped
    ms_sentence_short = [value for value in ms_sentence if value != '--']
    ms_sentence_short = [value for value in ms_sentence_short if value != '//']      
    #ms_sentence_short = [value for value in ms_sentence_short if value != '---']
    ms_disfl = ast.literal_eval(line[12])
    file_name = line[3].replace(".trans", "") + line[0]
    if file_name not in silver_corpus:
        silver_corpus[file_name] = [[], []]
    for i in range(len(ms_sentence_short)):
        # --- is a non-token with corresponding tags in other lists, whole entry must be skipped
        if ms_sentence_short[i] != '---':
            silver_corpus[file_name][0].append(ms_sentence_short[i])
            silver_corpus[file_name][1].append(ms_disfl[i])
    # Insert sentence boundary
    if ms_sentence_short != []:
        silver_corpus[file_name][0].append('XXXXXX')
        silver_corpus[file_name][1].append('XXXXXX')

# list of files in which A and B are swapped in silver transcripts (compared to MS-State)
keys = []
for key in sorted(ms_corpus):
    key_no_ab = key[0:6]
    if key_no_ab not in keys:
        keys.append(key_no_ab)

for k in keys:
    key_a = k + "A"
    key_b = k + "B"
    if k in swap:
        first_round = [key_a, key_b]
        second_round = [key_b, key_a]
    else:
        first_round = [key_a, key_a]
        second_round = [key_b, key_b]
    for key in [first_round, second_round]:
        skip_count = 0
        key_ms = key[0]
        key_silver = key[1]
        keys = key_ms + '\t' + key_silver
        count = 0
        silver_count = 0
        ms_count = 0
        # remove last occurrence of 'XXXXXX'
        if silver_corpus[key_silver][0][-1] == "XXXXXX":
            del silver_corpus[key_silver][0][-1]
            del silver_corpus[key_silver][1][-1]
        sentence_count = silver_corpus[key_silver][0].count('XXXXXX')
        for i in range(len(ms_corpus[key_ms][0]) + sentence_count):
            ms_word = ms_corpus[key_ms][0][i + ms_count].strip()
            start = ms_corpus[key_ms][1][i + ms_count].strip()
            end = ms_corpus[key_ms][2][i + ms_count].strip()
            try:
                silver_word = silver_corpus[key_silver][0][i + silver_count].strip()
                silver_tag = silver_corpus[key_silver][1][i + silver_count].strip()
            except:
                silver_word = "XX"
            try:
                silver_word_next = silver_corpus[key_silver][0][i + silver_count + 1].strip()
                silver_tag_next = silver_corpus[key_silver][1][i + silver_count + 1].strip()
            except:
                silver_word_next = "YY"
            try:
                ms_word_next = ms_corpus[key_ms][0][i + ms_count + 1].strip()
            except:
                ms_word_next = None
            if silver_word != "XXXXXX" and silver_word != "XX" and silver_tag == "XXXXXX":
                print "tag is XXXXXX:", silver_word
                sys.exit()
            # sentence boundaries 'XXXXXX' are translated to empty lines
            if silver_word == 'XXXXXX':
                print ""
                ms_count -= 1
            elif ms_word == silver_word:
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # e.g. don't == do+n't
            elif ms_word == silver_word+silver_word_next:
                print keys, '\t', ms_word, '\t', silver_word+silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            #e.g. cannot == can + ' ' + not
            elif ms_word == silver_word+' '+silver_word_next:
                print keys, '\t', ms_word, '\t', silver_word, ' ', silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            # i._b._m.'s
            elif re.match("([a-z]\._)*[a-z]\.'s", ms_word) and ms_word.replace(".", "").replace("_", "") == silver_word+silver_word_next:
                print keys, '\t', ms_word, '\t', silver_word, silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            # i._b._m.
            elif re.match("([a-z]\._)*[a-z]\.", ms_word) and ms_word.replace(".", "").replace("_", "") == silver_word:
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # o'clock vs. oclock
            elif ms_word.replace("'", "") == silver_word:
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            elif ms_word == "gonna" and silver_word == "going" and silver_word_next == "to":
                print keys, '\t', ms_word, '\t', silver_word, ' ', silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            elif ms_word == "wanna" and silver_word == "want" and silver_word_next == "to":
                print keys, '\t', ms_word, '\t', silver_word, ' ', silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            elif ms_word == "can't" and silver_word == "can" and silver_word_next == "n't":
                print keys, '\t', ms_word, '\tcan\'t\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            # check whether the next two words match
            # does not work if next token is "XXXXXX" since this is only a token in silver
            # this is why explicit if-clauses are following
            elif silver_word_next == ms_word_next \
                    or silver_word_next+"'s" == ms_word_next:
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2137 A.9
            elif ms_word == "relly" and silver_word == "ready":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2145 B
            elif ms_word == "storly" and silver_word == "story":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2184 B
            elif ms_word == "trest" and silver_word == "test":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2548 A.56
            elif ms_word == "what'n" and silver_word == "was" and silver_word_next == "n't":
                print keys, '\t', ms_word, '\t', silver_word+silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            # sw2662 A
            elif ms_word == "communercation" and silver_word == "communication":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2663 B.94
            elif ms_word == "wight" and silver_word == "right":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2709 A
            elif ms_word == "directle" and silver_word == "directed":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2818 B.68
            elif ms_word == "omniscious" and silver_word == "omniscent":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2818 B.68
            elif ms_word == "omniscipotent" and silver_word == "omnipotent":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw2887 A
            elif ms_word == "bacally" and silver_word == "basically":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3204 B
            elif ms_word == "yeam" and silver_word == "yeah":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3272 A
            elif ms_word == "u._s._r." and silver_word == "ussr":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3294 A
            elif ms_word == "bright" and silver_word == "right":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3296 A
            elif ms_word == "1" and silver_word == "pw65":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3513 B
            elif ms_word == "bamorghini" and silver_word == "lamborghini":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3524 B
            elif ms_word == "yack" and silver_word == "yeah":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3626 B
            elif ms_word == "maceboast" and silver_word == "mostly":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw3663 B
            elif ms_word == "doen't" and silver_word == "does" and silver_word_next == "n't":
                print keys, '\t', ms_word, '\t', silver_word, silver_word_next, '\t', silver_tag, silver_tag_next, '\t', start, '\t', end
                silver_count += 1
            # sw3675 B
            elif ms_word == "stale" and silver_word == "sale":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4109 A
            elif ms_word == "indivigal" and silver_word == "individual":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4168 A
            elif ms_word == "row" and silver_word == "wow":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4175 B
            elif ms_word == "unconvenient" and silver_word == "inconvenient":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4336 B
            elif ms_word == "pacifits" and silver_word == "specifics":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4618 B
            elif ms_word == "trests" and silver_word == "tests":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4703 A
            elif ms_word == "thrugs" and silver_word == "drugs":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4735 B
            elif ms_word == "rebil" and silver_word == "rehabilitate":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # sw4822 B
            elif ms_word == "splace" and silver_word == "space":
                print keys, '\t', ms_word, '\t', silver_word, '\t', silver_tag, '\t', start, '\t', end
            # skip MS-State words that are not in silver
            else:
                silver_count -= 1
                skip_count += 1
        print ""
        
        
        
        
        
        
