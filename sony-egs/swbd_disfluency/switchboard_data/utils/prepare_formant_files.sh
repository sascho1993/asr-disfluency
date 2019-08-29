cd /speech/dbwork/mul/spielwiese4/students/deschops/asr-disfluency/sony-egs/swbd_disfluency/switchboard_data/audio/formants/
mkdir csv_done
cd csv_unzip/csv_files

# Utterances had to be cut since DeepFormants couldn't handle files larger than 2s
# Now write all formant values for one utterance into one file
for file in sw*.csv; do basename=${file:0:15}; cat $file >> ../../csv_done/$basename.csv; done
cd ../..

rm -f formant_feats
# Write all formant feats into one file
for file in csv_done/* 
do
  cat $file | grep -v "NAME" >> formant_feats
done
