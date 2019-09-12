cd ../../swbd/s5c_split/exp/chain/tdnn7q_sp/decode_disfluency_silver_uttids_sw1_tg

# e.g. 7_0.0, where 7 is LMWT and 0.0 WIP
versions=`find . -name "score_*" | sed 's/\.\///g'`

cd ../../../../../../swbd_disfluency/switchboard_data

for version in $versions
do
  kaldi_output=../../swbd/s5c_split/exp/chain/tdnn7q_sp/decode_disfluency_silver_uttids_sw1_tg/$version/disfluency_silver_uttids_stm.ctm
  cat $kaldi_output | sort -s -k1,1 | python utils/get_kaldi_disfluency_labels_time_based.py > data/kaldi/$version
done
