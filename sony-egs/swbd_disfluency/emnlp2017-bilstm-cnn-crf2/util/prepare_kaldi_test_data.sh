# Prepare data for kaldi_test

. /speech/misc/com/software/sge/get-available-gpu/get-gpu-min-used-mem.sh

data=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data
nn=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/emnlp2017-bilstm-cnn-crf2
data_dir=data/kaldi_test

for file in $data/data/kaldi/*
do
  file_name=`echo $file | sed 's/\/speech\/dbwork\/mul\/spielwiese4\/students\/deschops\/asr-disfluency\/sony-egs\/swbd_disfluency\/switchboard_data\/data\/kaldi\///g'`
  python $data/utils/get_duration_features.py $file > $nn/$data_dir/$file_name
done

cd $nn

for file in $data_dir/score_*
do
  echo "Preparing" $file
  version=`echo $file | sed 's/.*\///g'`
  python RunModel_CoNLL_Format_POS.py models/unidep_pos/unidep_pos_0.9576_0.9556_18.h5 $file > $data_dir/$version.pos_tags
  paste $data_dir/$version.pos_tags $file | awk -F '\t' '{print $3, $4, $5, $2, $6, $7, $8}' | tr ' ' '#' | sed 's/##/#/g' | sed 's/###//g' | tr '#' '\t' > $data_dir/$version.done
  python util/split_train_dev_test_kaldi.py $data_dir/$version.done data/kaldi_test
done


python util/load_prosodic_data_kaldi.py $data/data/kaldi test=True

