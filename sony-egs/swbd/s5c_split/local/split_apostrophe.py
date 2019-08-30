#!/usr/bin/env python

# Copyright 2019  Sarah Schopper


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', help='Input lexicon',required=True)
args = parser.parse_args()


fin_lex = open(args.input,"r")


print "\'s z"
print "\'s s"
print "\'s ih z"
print "n't en t"
print "n't ih n t"
print "n'ts n t s"
print "n'ts en t s"
print "'ve v"
print "'ve ax v"
print "'m m"
print "'ll l"
print "'ll ax l"
print "'d d"
print "'d ih d"
print "n'ts n t s"
print "n'ts en t s"
print "'re r"
print "'re er"

keep_lex = []
#apostrophes = []
for lex in fin_lex:
    items = lex.split()
    word = items[0]
    pron = lex[len(items[0])+1:].strip()
    if word[-2:] == '\'s':
        if word[:-2] not in keep_lex:
            # ross's, ex's
            if ((word[-3] == 's' or word[-3] == 'x' and pron[-4:] == 'ih z')\
                    # price's, rose's, porshe's, judge's
                    or (word[-3] == 'e' and (pron[-6:] == 's ih z'\
                        or pron[-6:] == 'z ih z' or pron[-7:] == 'sh ih z' or pron[-7:] == 'jh ih z'))\
                    # coach's, british's
                    or ((word[-4:-3] == 'sh' or word[-4:-3] == 'ch') and (pron[-7:] == 'sh ih z' or pron[-7:] == 'ch ih z'))):
                #fout_lex.write(word[:-2] + ' ' + pron[:-4] + '\n')
                #apostrophes.append(word)
                print word[:-2] + ' ' + pron[:-4]
            elif word[-3] == '-':
                print word + ' ' + pron
            elif (pron[-1] == 's' or pron[-1] == 'z'):
                print word[:-2] + ' ' + pron[:-2]
            else:
                print word[:-2] + ' ' + pron
    elif word == "-n't":
        pass
    elif word == "in't":
        print "i ih"
    elif word[-3:] == 'n\'t':
        if pron [-6:] == "ih n t":
            print word[:-3] + ' ' + pron[:-7]
        elif pron[-4:] == "en t":
            print word[:-3] + ' ' + pron[:-5]
        elif pron[-3:] == "n t":
            print word[:-3] + ' ' + pron[:-4]
    elif word[-3:] == '\'ve':
        if pron[-4:] == "ax v":
            print word[:-3] + ' ' + pron[:-5]
        elif pron [-1:] == "v":
            print word[:-3] + ' ' + pron[:-2]
    elif word[-3:] == '\'re':
        if pron[-2:] == "er":
            print word[:-3] + ' ' + pron[:-3]
        elif pron [-1:] == "r":
            print word[:-3] + ' ' + pron[:-2]
    elif word[-3:] == '\'ll':
        if pron[-4:] == "ax l":
            print word[:-3] + ' ' + pron[:-5]
        elif pron [-1:] == "l":
            print word[:-3] + ' ' + pron[:-2]
    elif word[-2:] == '\'d':
        if pron[-4:] == "ax d":
            print word[:-2] + ' ' + pron[:-5]
        elif pron [-1:] == "d":
            print word[:-2] + ' ' + pron[:-2]
    elif word == "i'm" or word[-4:] == "n'ts":
        pass
    else:
    	keep_lex.append(word)
    	print word + ' ' + pron

#print apostrophes
#print keep_lex


    
