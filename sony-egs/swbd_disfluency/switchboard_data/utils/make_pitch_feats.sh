kaldi_dir=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split
sw_dir=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data

cd $kaldi_dir
. ./path.sh
compute-and-process-kaldi-pitch-feats --sample-frequency=8000 scp:$sw_dir/audio/helpers/wav.scp ark,t:$sw_dir/audio/F0/pitch_feats

compute-kaldi-pitch-feats --sample-frequency=8000 scp:$sw_dir/audio/helpers/wav.scp ark,t:$sw_dir/audio/F0/raw_pitch


cd $sw_dir

cat audio/F0/pitch_feats | tr -d '\n' | sed 's/   / /g'| sed 's/  / /g' | tr ']' '\n' | sed 's/$/]/g' | sed 's/ /, /g' | sed 's/, \]/ ]/g' | sed 's/\[, /[ /g' > audio/F0/pitch_feats_for_python
