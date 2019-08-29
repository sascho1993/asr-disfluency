"""
Outputfile is a list of all words that occur in silver transcripts
The list is not used for further processing but provides a way to 'sanity check' the silver transcripts
"""

import sys
import ast

silver = sys.stdin.readlines()
ab_swap = open(sys.argv[1], "r")
silver_words = open(sys.argv[2], "w")

    
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
swap = []
for line in ab_swap:
    swap.append(line.strip())
print swap

keys = []
for key in sorted(silver_corpus):
    key_no_ab = key[0:6]
    if key_no_ab not in keys:
        keys.append(key_no_ab)

for k in keys:
    if k in swap:
        key_a = k + "B"
        key_b = k + "A"
    else:
        key_a = k + "A"
        key_b = k + "B"
    for i in range(len(silver_corpus[key_a][0])):
        if silver_corpus[key_a][0][i] != "XXXXXX":
            silver_words.write(key_a + '\t' + silver_corpus[key_a][0][i] + '\t' + silver_corpus[key_a][1][i] + '\n')
        else:
            # sentence boundaries 'XXXXXX' are translated to empty lines
            silver_words.write('\n')
    for i in range(len(silver_corpus[key_b][0])):
        if silver_corpus[key_b][0][i] != "XXXXXX":
            silver_words.write(key_b + '\t' + silver_corpus[key_b][0][i] + '\t' + silver_corpus[key_b][1][i] + '\n')
        else:
            silver_words.write('\n')



        
        


