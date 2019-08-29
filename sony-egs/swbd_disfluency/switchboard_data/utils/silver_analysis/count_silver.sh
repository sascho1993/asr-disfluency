#!/bin/bash

cat switchboard_corrected_with_silver_reannotation.tsv | sed 's/""/"/g' | python count_silver.py

#cat test.txt | sed 's/""/"/g' | python count_silver.py
