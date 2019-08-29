""" 
In the silver transcripts, apostrophes are separated from the previous word (e.g. I 'm. does n't)
However, the MS-State transcripts don't separate the two and therefore do not provide time stamps for the second part.
This scripts adds time stamps to all those cases. The added time stamps are guessed based on the part-word length ratio.
"""

import sys
from math import trunc, ceil

f = open(sys.argv[1], "r")

prev_file_id = ""
for line in f:
    try:
        file_id, word, tag, start, end = line.split("\t")
        if prev_file_id != file_id:
            file_id_count = 1
        prev_file_id = file_id
        file_utt_number = file_id + "_utt_" + str(file_id_count).zfill(3)
        start = int(start)
        end = int(end)
        # does n't
        word = word.replace(" ", "")
        if (word.strip()[-2:] == "'s" or word.strip()[-2:] == "'d" or word.strip()[-2:] == "'m") and len(word.strip()) > 2:
            # For acronyms (e.g. v._c._r.'s) each letter should get the duration of two letters
            # since the letters consist of two phonemes most of the time
            # leaving "_" would mean that they are assigned the same length as 3 characters
            word_acronym = word.replace("_", "")
            word_length = int(end) - int(start)
            # length of word without apostrophe
            num_chars = len(word_acronym) - 1
            dur_per_char = float(word_length)/num_chars
            dur_second_part = 1 * dur_per_char
            dur_second_part = round(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\t', word[:-2], '\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\t', word[-2:], '\t', second_tag, '\t', second_start, '\t', end
        elif (word.strip()[-3:] == "'re" or word.strip()[-3:] == "'ve" or word.strip()[-3:] == "'ll") and len(word.strip()) > 3:
            word_length = int(end) - int(start)
            # length of word without apostrophe
            num_chars = len(word) - 2
            dur_per_char = float(word_length)/num_chars
            # 're, 've and 'll only have one phoneme (or two with a very reduced schwa)
            dur_second_part = 1 * dur_per_char
            dur_second_part = round(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\t', word[:-3], '\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\t', word[-3:], '\t', second_tag, '\t', second_start, '\t', end
        elif word.strip()[-3:] == "n't" and len(word.strip()) > 3:
            word_length = int(end) - int(start)
            # length of word without apostrophe
            num_chars = len(word) - 2
            dur_per_char = float(word_length)/num_chars
            dur_second_part = 2 * dur_per_char
            dur_second_part = round(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\t', word[:-3], '\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\t', word[-3:], '\t', second_tag, '\t', second_start, '\t', end
        # special cases that have to be split again because the two BIO-tags don't match
        # gonna and wanna are split into "going to" and "want to" respectively in order to get trained word embeddings
        elif word.strip() == "y'all":
            word_length = int(end) - int(start)
            dur_second_part = (1/4) * word_length
            dur_second_part = round(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\ty\'\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\tall\t', second_tag, '\t', second_start, '\t', end
        elif word.strip() == "cannot":
            word_length = int(end) - int(start)
            dur_second_part = (1/2) * word_length
            # first syllable is stressed and therefore rather longer than second
            dur_second_part = trunc(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\tcan\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\tnot\t', second_tag, '\t', second_start, '\t', end
        elif word.strip() == "gonna":
            word_length = int(end) - int(start)
            dur_second_part = (1/2) * word_length
            # first syllable is stressed and therefore rather longer than second
            dur_second_part = trunc(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\tgoing\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\tto\t', second_tag, '\t', second_start, '\t', end
        elif word.strip() == "wanna":
            word_length = int(end) - int(start)
            dur_second_part = (1/2) * word_length
            # first syllable is stressed and therefore rather longer than second
            dur_second_part = trunc(dur_second_part)
            second_start = int(end - dur_second_part)
            first_tag, second_tag = tag.strip().split(' ')
            print file_utt_number, '\t', file_id, '\twant\t', first_tag, '\t', start, '\t', second_start
            print file_utt_number, '\t', file_id, '\tto\t', second_tag, '\t', second_start, '\t', end
        else:
            print file_utt_number, '\t', file_id, '\t', word, '\t', tag, '\t', start, '\t', end
    except:
        file_id_count += 1
        print ""
    
