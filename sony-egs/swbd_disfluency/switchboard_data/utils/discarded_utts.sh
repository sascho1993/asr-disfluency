cat data/silver_wd/ms_silver_word_time_stamps | awk -F '\t' '$5==$6 {print $1}' | sort | uniq > audio/helpers/utt_word_zero_dur
cat audio/helpers/utt_word_zero_dur audio/helpers/utts_zero_dur | sort | uniq | grep "sw" > audio/helpers/discarded_utts

