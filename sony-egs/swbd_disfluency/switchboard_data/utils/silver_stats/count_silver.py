import sys
import ast

#f = open("switchboard_single_quote", "r")
f = sys.stdin.readlines()

c = 0
difference = 0
for line in f:
    if c == 0:
        c += 1
        continue
    line = line.split('\t')
    sentence = ast.literal_eval(line[4].strip('"'))
    ms_sentence = ast.literal_eval(line[5].strip('"'))
    ms_length_before = len(ms_sentence)
    ms_sentence_short = [value for value in ms_sentence if value != '--']
    ms_sentence_short = [value for value in ms_sentence_short if value != '//']
    #print ms_sentence_short
    #print difference
    comb_sentence = ast.literal_eval(line[6].strip('"'))
    names = ast.literal_eval(line[7])
    ms_names = ast.literal_eval(line[8])
    comb_ann = ast.literal_eval(line[9])
    tags = ast.literal_eval(line[10])
    ms_disfl = ast.literal_eval(line[12])
    f_name = line[3].replace(".trans", "")+ line[0] + "\t" + line[0] + "." + line[1].replace(".0", "") + "\tutt" + line[2]
    #print f_name
    # assumption: len(sentence) = len(tags), len(ms_sentence) = len(ms_disfl), len(comb_sentence) = len(comb_ann)
    print f_name, '\t', len(sentence),'\t', len(ms_sentence_short),'\t', len(comb_sentence), '\t', len(tags), '\t', len(ms_disfl), '\t', len(comb_ann)
    difference = 0
    
    
