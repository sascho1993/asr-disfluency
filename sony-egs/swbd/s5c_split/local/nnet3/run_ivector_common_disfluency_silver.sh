#!/bin/bash

. ./cmd.sh
set -e
stage=1
train_stage=-10
generate_alignments=true
speed_perturb=true

. ./path.sh
. ./utils/parse_options.sh

mkdir -p exp/nnet3
#train_set=train_nodup

#if [ -e data/rt03 ]; then maybe_rt03=rt03; else maybe_rt03= ; fi

if $speed_perturb; then


if [ $stage -le 1 ]; then
  mfccdir=mfcc_hires
#  if [[ $(hostname -f) == *.clsp.jhu.edu ]] && [ ! -d $mfccdir/storage ]; then
#    date=$(date +'%m_%d_%H_%M')
#    utils/create_split_dir.pl /export/b0{1,2,3,4}/$USER/kaldi-data/mfcc/swbd-$date/s5b/$mfccdir/storage $mfccdir/storage
#  fi

  # the 100k_nodup directory is copied seperately, as
  # we want to use exp/tri2_ali_100k_nodup for lda_mllt training
  # the main train directory might be speed_perturbed
#  for dataset in $train_set train_100k_nodup; do
#    utils/copy_data_dir.sh data/$dataset data/${dataset}_hires

#    utils/data/perturb_data_dir_volume.sh data/${dataset}_hires

#    steps/make_mfcc.sh --nj 70 --mfcc-config conf/mfcc_hires.conf \
#        --cmd "$train_cmd" data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
#    steps/compute_cmvn_stats.sh data/${dataset}_hires exp/make_hires/${dataset} $mfccdir;

    # Remove the small number of utterances that couldn't be extracted for some
    # reason (e.g. too short; no such file).
#    utils/fix_data_dir.sh data/${dataset}_hires;
#  done

  for dataset in disfluency_silver; do
    # Create MFCCs for the eval set
    utils/copy_data_dir.sh data/$dataset data/${dataset}_hires
    steps/make_mfcc.sh --cmd "$train_cmd" --nj 10 --mfcc-config conf/mfcc_hires.conf \
        data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
    steps/compute_cmvn_stats.sh data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
    utils/fix_data_dir.sh data/${dataset}_hires  # remove segments with problems
  done

  # Take the first 30k utterances (about 1/8th of the data) this will be used
  # for the diagubm training
#  utils/subset_data_dir.sh --first data/${train_set}_hires 30000 data/${train_set}_30k_hires
#  utils/data/remove_dup_utts.sh 200 data/${train_set}_30k_hires data/${train_set}_30k_nodup_hires  # 33hr
fi



if [ $stage -le 2 ]; then
  # We extract iVectors on all the train_nodup data, which will be what we
  # train the system on.

  # having a larger number of speakers is helpful for generalization, and to
  # handle per-utterance decoding well (iVector starts at zero).
#  utils/data/modify_speaker_info.sh --utts-per-spk-max 2 data/${train_set}_hires data/${train_set}_max2_hires

#  steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 30 \
#    data/${train_set}_max2_hires exp/nnet3/extractor exp/nnet3/ivectors_$train_set || exit 1;

  for data_set in disfluency_silver; do
    steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 30 \
      data/${data_set}_hires exp/nnet3/extractor exp/nnet3/ivectors_$data_set || exit 1;
  done
fi

fi

exit 0;
