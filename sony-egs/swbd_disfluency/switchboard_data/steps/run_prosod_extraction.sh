#!/bin/bash

# Extract Pitch features
sh utils/make_pitch_feats.sh

# Extract Energy features
sh utils/make_fbank_feats.sh

# Prepare formant files
sh utils/prepare_formant_files.sh


# Prepare duration features based on fluent words only (no RM, no RR, no non-lexical conversational fillers)

# Kaldi directory in which alignments are generated
mkdir /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split/data/disfluency_fluent_words

# Get word durations of MS-State transcripts (all files, not only PennTreebank portion)
sh utils/prepare_all_ms_words.sh audio/duration_feats

# create Kaldi files for fluent speech data
python utils/get_duration_fluent_speech.py

# Create alignment file and get phone durations
sh get_kaldi_phone_durations_fluent.sh


# Creates new version of silver transcripts: ms_silver_durations_fluent_words
python utils/get_duration_features.py audio/duration_feats/kaldi_ali_phones_only_fluent > data/silver_wd/ms_silver_durations_fluent_words


==================================================================================================================
============= Not used ===========================================================================================
==================================================================================================================
# Get phone durations with Kaldi from laignment file (for all speech, also disfluent and filler words)
sh utils/get_kaldi_phone_durations.sh

# Creates new version of silver transcripts: ms_silver_with_durations
python utils/get_duration_features.py audio/duration_feats/kaldi_ali_phones > data/silver_wd/ms_silver_with_durations
