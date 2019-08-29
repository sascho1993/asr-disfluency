import sys
import ast

#f = open("switchboard_for_python", "r")
f = sys.stdin.readlines()

c = 0
for line in f:
    tree_counter = 0
    if c == 0:
        c += 1
        continue
    line = line.split('\t')
    sentence = ast.literal_eval(line[4].strip('"'))
    ms_sentence = ast.literal_eval(line[5].strip('"'))
    ms_length_before = len(ms_sentence)
    ms_sentence_short = [value for value in ms_sentence if value != '--']
    ms_sentence_short = [value for value in ms_sentence_short if value != '//']
    comb_sentence = ast.literal_eval(line[6].strip('"'))
    names = ast.literal_eval(line[7])
    ms_names = ast.literal_eval(line[8])
    comb_ann = ast.literal_eval(line[9])
    tags = ast.literal_eval(line[10])
    ms_disfl = ast.literal_eval(line[12])
    f_name = line[3].replace(".trans", "")+ line[0] + "\t" + line[0] + "." + line[1].replace(".0", "") + "\tutt" + line[2]
    
    for i in range(len(comb_sentence)):
        if comb_sentence[i] == '//' or comb_sentence[i] == '---' or comb_sentence[i] == '--':
            tree_counter += 1
            continue
        if ms_disfl != []:
            if comb_ann[i] == 'O':
                print f_name, '\t', comb_sentence[i], '\t', comb_ann[i],'\t', ms_disfl[i-tree_counter]
            elif comb_ann[i] == 'INS':
                tree_counter += 1
            elif comb_ann[i] == 'DEL':
                print f_name, '\t', comb_sentence[i], '\t', comb_ann[i],'\t', ms_disfl[i-tree_counter]
            elif comb_ann[i] == 'SUB_TREE':
                tree_counter += 1
            elif comb_ann[i] == 'SUB_MS':
                print f_name, '\t', comb_sentence[i], '\t', comb_ann[i],'\t', ms_disfl[i-tree_counter]
            elif comb_ann[i] == 'CONT_TREE':
                tree_counter += 1
            elif comb_ann[i] == 'CONT_MS':
                print f_name, '\t', comb_sentence[i], '\t', comb_ann[i],'\t', ms_disfl[i-tree_counter]
    print ""
