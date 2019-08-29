silver_dir=data/silver_wd

# Split words (e.g. it's -> it 's) and invent time stamps
python add_timestamps_for_kaldi.py $silver_dir/reverse_comparison_out audio/helpers/discarded_utts > $silver_dir/ms_silver_for_kaldi

# Generate Kaldi files in KALDI_DIR/data/disfluency_silver_uttid
python utils/prepare_data_for_kaldi.py

cd /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_no_fragments
. ./cmd.sh
. ./path.sh
. utils/parse_options.sh

cat wav.scp | sed 's/^sw0/sw/g' > wav_scp
rm -f wav.scp
mv wav_scp wav.scp

# Generate spk2utt
perl utils/utt2spk_to_spk2utt.pl data/disfluency_silver_uttid/utt2spk  > data/disfluency_silver_uttid/spk2utt
utils/fix_data_dir.sh data/disfluency_silver_uttid

# Make MFCC feats
steps/make_mfcc.sh --nj 50 --cmd "$train_cmd"  data/disfluency_silver exp/make_mfcc/disfluency_silver_uttid mfcc
steps/compute_cmvn_stats.sh data/disfluency_silver_uttid exp/make_mfcc/disfluency_silver_uttid mfcc
utils/fix_data_dir.sh data/disfluency_silver_uttid
mv data/disfluency_silver_uttid/segments data/disfluency_silver_uttid/segments_bak

cat data/disfluency_silver_uttid/segments_bak | awk '$3!=$4 {print}' > data/disfluency_silver_uttid/segments 

# Decode silver data
steps/decode_fmllr.sh --nj 30 --cmd "$decode_cmd" --config conf/decode.config exp/chain/tdnn7q_sp/graph_sw1_tg data/disfluency_silver_uttid exp/chain/tdnn7q_sp/decode_disfluency_silver_sw1_tg

# Generate Disfluency labels for Kaldi output based on time overlap with silver disfluency labels
sh utils/get_kaldi_disfluency_labels_time_based.sh
