silver_dir=data/silver_wd
silver_orig=data/silver_transcript

# Run Kaldi scripts to prepare MS-State data
sh utils/prepare_ms_words.sh

# Get a list of files in which speaker ids of MS-State and Treebank are swapped
cat $silver_orig/switchboard_corrected_with_silver_reannotation.tsv | sed 's/""/"/g' | \
	python utils/get_a_b_swap.py $silver_dir/words $silver_dir/a_b_swap

# Get a list of silver words and their disfluency tags (used to make sure the following scripts work correctly)
cat $silver_orig/switchboard_corrected_with_silver_reannotation.tsv | sed 's/""/"/g' | python utils/get_silver_word_list.py $silver_dir/a_b_swap $silver_dir/silver_words

# Forward comparison of MS-State and Treebank words
cat $silver_orig/switchboard_corrected_with_silver_reannotation.tsv | sed 's/""/"/g' | \
	python utils/compare_silver_ms.py $silver_dir/words $silver_dir/a_b_swap > $silver_dir/compare_ms_silver

# Backward comparison of MS-State and Treebank words (to make sure right time stamps are chosen)
python utils/reverse_comparison_ms_silver.py $silver_dir/compare_ms_silver $silver_dir/words > $silver_dir/reverse_comparison_out

# Split words (e.g. it's -> it 's) and invent time stamps
python utils/add_timestamps_apostrophe.py $silver_dir/reverse_comparison_out > $silver_dir/ms_silver_comparison_done

# Cut switchboard sph files into utterances with sentence boundaries taken from silver transcripts and time stamps from MS-State
cut_audio_silver.sh

# DeepFormants can only work with files up to 2 sec, This script splits larger files into subfiles
#python utils/trim_switchboards_data.py

# Get a list of utterances that are discarded because words are of length 0
sh utils/discarded_utts.sh

# Split words (e.g. it's -> it 's) and invent time stamps, set start time back to 0 for each utterance that was cut above
python utils/add_timestamps_apostrophe_for_cut_files.py $silver_dir/reverse_comparison_out audio/helpers/discarded_utts | uniq > $silver_dir/ms_silver_word_time_stamps
