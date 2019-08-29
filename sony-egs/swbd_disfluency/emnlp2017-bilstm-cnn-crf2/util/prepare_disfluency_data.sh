# Prepare train.txt, dev.txt, test.txt for data/disfluency

data_dir="data/disfluency"

mkdir -p $data_dir
cat ../switchboard_data/labeled/switchboard_prepared_BIO | uniq > $data_dir/switchboard_prepared_BIO

python RunModel_CoNLL_Format.py models/unidep_pos/unidep_pos_0.9576_0.9556_18.h5 data/disfluency/switchboard_prepared_BIO > $data_dir/switchboard_pos

paste $data_dir/switchboard_pos $data_dir/switchboard_prepared_BIO | awk -F '\t' '{print $3, $4, $5, $6, $7, $8, $2, $9}' | tr ' ' '\t' | tr '\t' '#' | sed 's/#######//g' | tr '#' '\t' > $data_dir/switchboard_pos_marker

python util/add_markers.py data/disfluency/switchboard_pos_marker $data_dir/switchboard_all_prepared

python util/split_train_dev_test.py data/disfluency/switchboard_all_prepared $data_dir
