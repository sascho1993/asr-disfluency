"""
Writes duration of longest word in dataset to stdout
This max duration is used to generate prosodic feats (e.g. in emnlp2017-bilstm-cnn-crf2/util/load_prosodic_data.py)
and for the Input layer of the prosodic features in emnlp2017-bilstm-cnn-crf2/neuralnets/BiLSTM.py

Usage:
  python max_dur.py data/silver_ws/ms_silver_ms_silver_comparison_done
"""

import sys

f = open(sys.argv[1], "r")

start_time = ""
max_dur = 0
for line in f:
    try:
        file_id, file_name, word, tag, start, end = line.split()
        end = int(end.strip())
        start = int(start)
        dur = end-start
        if dur > max_dur:
            max_dur = dur
    except:
        pass
print max_dur
