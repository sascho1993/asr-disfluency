# Prepare data for several versions of kaldi output 

sw_data=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data

versions="7_0.0 17_1.0"

for version in $versions
do
  mkdir -p data/$version
  cp data/kaldi_test/score_$version.done data/$version
  python util/split_train_dev_test.py data/$version/score_$version.done data/$version
  python util/load_prosodic_data_kaldi.py data/$version test=False
done

