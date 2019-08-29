# Get transcripts from dialogAct corpus and preprocess them
# output: data/raw_text/all_utts
#sh utils/data_preprocessing_dialogAct.sh

# step inbetween: manual corrections in all_utts_man

# remove spacing inconsistencies in all_utts_man
# output: all_uts_clean_split
sh clean_data.sh

# parse all_uts_clean_split and return a BIO tagged file with one word per line
python prepare_data_BIO.py
