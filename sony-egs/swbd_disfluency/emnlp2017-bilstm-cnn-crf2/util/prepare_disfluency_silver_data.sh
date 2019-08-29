# Prepare train.txt, dev.txt, test.txt for data/disfluency_silver

data_dir="data/disfluency_silver"

mkdir -p $data_dir
cat ../switchboard_data/data/silver_wd/ms_silver_word_time_stamps | uniq > $data_dir/ms_silver_word_time_stamps

python RunModel_CoNLL_Format.py models/unidep_pos/unidep_pos_0.9576_0.9556_18.h5 $data_dir/ms_silver_word_time_stamps > $data_dir/pos_tags

paste $data_dir/pos_tags $data_dir/ms_silver_word_time_stamps | awk -F '\t' '{print $3,$5,$6,$2}' | tr ' ' '#' | sed 's/##/#/g' | sed 's/##//g' | tr '#' '\t' > $data_dir/switchboard_done

python util/split_train_dev_test.py $data_dir/switchboard_done $data_dir
