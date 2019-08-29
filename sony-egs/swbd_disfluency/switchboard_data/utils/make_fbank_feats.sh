cd /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd/s5c_split
. path.sh

compute-fbank-feats --num-mel-bins=40 --sample-frequency=8000 --use-energy=true scp:/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/helpers/wav.scp ark,t:/speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/energy/fbank40_energy
