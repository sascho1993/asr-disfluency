kaldi_dir=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split
audio_dir=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio

# Extract Pitch features
sh make_pitch_feats.sh

# Extract Energy features
sh make_fbank_feats.sh

# Extract Energy features
sh prepare_formant_files.sh


# duration features based on fluent words only (no RM, no RR, no non-lexical conversational fillers)
mkdir $kaldi_dir/data/disfluency_fluent_words

# Create Kaldi data files in data/disfluency_fluent_words
python get_duration_fluent_speech.py

# Create alignment file and get phone durations
sh utils/get_kaldi_fluent_phone_durations.sh

# Get word durations of MS-State transcripts (all files, not only PennTreebank portion)
sh utils/prepare_all_ms_words.sh audio/duration_feats

# Get new dataset containing durations features
python get_duration_features.py audio/duration_feats/kaldi_ali_phones_only_fluent > data/silver_wd/ms_silver_durations_fluent_words


==================================================================================================
============ duration feature based on all MS-State words ========================================
==================================================================================================

# Get phone durations from kaldi alignment file
sh utils/get_kaldi_phone_durations.sh

# Get word durations of MS-State transcripts (all files, not only PennTreebank portion)
sh utils/prepare_all_ms_words.sh audio/duration_feats

# Creates new version of silver transcripts: ms_silver_with_durations
python utils/get_duration_features.py > data/silver_wd/ms_silver_with_durations

# Get new dataset containing durations features
python get_duration_features.py audio/duration_feats/kaldi_ali_phones > data/silver_wd/ms_silver_with_durations
