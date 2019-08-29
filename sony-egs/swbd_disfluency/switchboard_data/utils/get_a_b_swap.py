"""
Comparing the PennTreebank and the MsState transcripts, the speaker assignment is often swapped.
This means that speaker A in PennTreebank corresponds to speaker B in MsState and vice versa.
This script compares the bag of words of the Treebank and the MsState transcript for each file, e.g.:
1) sw2005A(treebank) - sw2005A(MsState) + sw2005B(treebank) - sw2005B(MsState)
2) sw2005A(treebank) - sw2005B(MsState) + sw2005B(treebank) - sw2005A(MsState),
where '-' denoted the symmetric difference between the two sets.
If the cross-difference as in 2) is smaller, the file name is written into an output file.

Usage:
  cat $silver_orig/switchboard_corrected_with_silver_reannotation.tsv | sed 's/""/"/g' | \
        python utils/get_a_b_swap.py $silver_dir/words $silver_dir/a_b_swap
"""

import sys
import ast

silver = sys.stdin.readlines()
ms = open(sys.argv[1], "r")
ab_swapped = open(sys.argv[2], "w")

ms_corpus = {}
for line in ms:
    file_id, word = line.split()
    file_id = file_id[0:2] + file_id[3:7] + file_id[8:9]
    if file_id not in ms_corpus:
        ms_corpus[file_id] = set()
    ms_corpus[file_id].add(word)
    
c = 0
silver_corpus = {}
for line in silver:
    # skip header
    if c == 0:
        c += 1
        continue
    line = line.split('\t')
    ms_sentence = ast.literal_eval(line[5].strip('"'))
    ms_sentence_short = [value for value in ms_sentence if value != '--']
    ms_sentence_short = [value for value in ms_sentence_short if value != '//']
    file_name = line[3].replace(".trans", "") + line[0]
    if file_name not in silver_corpus:
        silver_corpus[file_name] = {}
        silver_corpus[file_name] = set()
    silver_corpus[file_name].update(ms_sentence_short)

keys = []
for key in sorted(ms_corpus):
    key_no_ab = key[0:6]
    if key_no_ab not in keys:
        keys.append(key_no_ab)
       
for key in keys:
    key_a = key + "A"
    key_b = key + "B"
    diff_a_a = silver_corpus[key_a].symmetric_difference(ms_corpus[key_a])
    diff_b_b = silver_corpus[key_b].symmetric_difference(ms_corpus[key_b])
    diff_a_b = silver_corpus[key_a].symmetric_difference(ms_corpus[key_b])
    diff_b_a = silver_corpus[key_b].symmetric_difference(ms_corpus[key_a])
    diff_same = len(diff_a_a) + len(diff_b_b)
    diff_swap = len(diff_a_b) + len(diff_b_a)
    if diff_same > diff_swap:
        ab_swapped.write(key + '\n')
    


