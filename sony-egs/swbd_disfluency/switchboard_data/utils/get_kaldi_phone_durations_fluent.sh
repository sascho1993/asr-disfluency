# Outputs:
#   - lexicon.txt -- kaldi lexicon with added pronunciations for silver words
#   - kaldi_ali_phones -- phone alignment file with phone length in frames

sw_data=/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data

cd /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split

. ./cmd.sh
. ./path.sh
. utils/parse_options.sh

# Create spk2utt file
perl utils/utt2spk_to_spk2utt.pl data/disfluency_fluent_words/utt2spk > data/disfluency_fluent_words/spk2utt

# Create forced alignments for fluent words
steps/align_fmllr.sh --nj 1 --cmd "$train_cmd" \
                         data/disfluency_fluent_words data/lang exp/tri4 data/disfluency_fluent_words

cp exp/tri4/phones.txt $sw_data/audio/duration_feats/
cp data/local/dict/lexicon.txt $sw_data/audio/duration_feats/lexicon_kaldi.txt

# add entries to the lexicon that are in silver but not in MS-State
echo "y' y" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "emancipation ih m ae n s ih p ey sh ih n" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "omniscent aa m n ih sh ih n t" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "omnipotent aa m n ih p ax t ih n t" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
# Error in silver transcripts, supposed  to be '1'
echo "pw65 w ah n" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "lamborghini l ae m b er g iy n iy" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "mir m iy r" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "inequality ih n iy k w ax l ih t iy" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "assumably ax s uw m ax b l iy" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "excavators eh k s ax v ey t er s" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "grievous g r iy v iy ih s" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt
echo "telecredit t eh l ih k r eh d ih t" >> $sw_data/audio/duration_feats/lexicon_kaldi.txt

cat $sw_data/audio/duration_feats/lexicon_kaldi.txt | sort > $sw_data/audio/duration_feats/lexicon.txt
rm -f $sw_data/audio/duration_feats/lexicon_kaldi.txt

# Get phone alignment file with phone length in frames
ali-to-phones --write-lengths exp/tri4/final.mdl "ark:gunzip -c data/disfluency_fluent_words/ali.1.gz |" ark,t:- >> $sw_data/audio/duration_feats/kaldi_ali_phones_only_fluent


