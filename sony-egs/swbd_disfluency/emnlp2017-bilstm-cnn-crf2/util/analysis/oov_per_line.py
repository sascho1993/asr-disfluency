#!/usr/bin/env python

vocab = open("vocab_dev", "r")
komninos = open("komninos_vocab", "r", encoding='utf-8')

komninos_list = []
for word in komninos:
    try:
        komninos_list.append(word.strip())
    except:
        pass

vocab_list = []
for word in vocab:
    vocab_list.append(word.strip())
    

for word in vocab_list:
    if word not in komninos_list and word != "":
        print (word, "\toov")
    elif word in komninos_list and word != "":
        print (word, "\tin_voc")
    else:
        print (word)
