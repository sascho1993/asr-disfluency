#!/usr/bin/env python

vocab = open("vocab", "r")
komninos = open("komninos_vocab", "r", encoding='utf-8')

komninos_list = []
for word in komninos:
    try:
        komninos_list.append(word.lower().strip())
    except:
        pass

vocab_list = []
for word in vocab:
    vocab_list.append(word.strip())

for word in vocab_list:
    if word.strip() not in komninos_list and word != "":
        print (word)
