# Prepare train.txt, dev.txt, test.txt for data/disfluency_duration

data_dir="data/disfluency_duration"

cp /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/data/silver_wd/ms_silver_with_durations $data_dir

#python RunModel_CoNLL_Format.py models/unidep_pos/unidep_pos_0.9576_0.9556_18.h5 $data_dir/ms_silver_word_time_stamps > $data_dir/pos_tags
cp data/disfluency_silver/pos_tags $data_dir

paste $data_dir/pos_tags $data_dir/ms_silver_with_durations | awk -F '\t' '{print $3, $4, $5, $2, $6, $7, $8}' | tr ' ' '#' | sed 's/##/#/g' | sed 's/###//g' | tr '#' '\t' > $data_dir/switchboard_done

python util/split_train_dev_test.py $data_dir/switchboard_done $data_dir
