#!/bin/bash

# Cut Switchboard files into utterances
# output:
#   - audio/wav -- directory which contains one wav file per utterance
#   - audio/helpers/wav.scp -- scp file for Kaldi
#   - audio/helpers/utts_zero_dur -- list of utterances that were discarded since they are too short

# write utt_id with start and end time into file if start != end
cat data/silver_wd/ms_silver_comparison_done | sed ':a;N;$!ba;s/\n\n/#/g' | tr -d '\n' | tr '#' '\n' | awk -F '\t' -v OFS='\t' '$5 != $NF {print $1, $5, $NF}' > audio/helpers/silver_utts

rm -f audio/helpers/wav.scp
rm -f audio/helpers/discarded_utts

mkdir -p audio/wav

cat audio/helpers/silver_utts | while read line
do
  file_name=`echo $line | awk -F ' ' '{print $1}'`
  file_number=${file_name:2:4}
  start=`echo $line | awk -F ' ' '{print $2}'`
  start_sec=`bc <<< "scale=2; $start/100"`
  end=`echo $line | awk -F ' ' '{print $3}'`
  end_sec=`bc <<< "scale=2; $end/100"`
  diff=$(echo "($end-$start)" | bc -l)
  channel=${file_name:6:1}
  sph=`find /speech/db/SpeechCorpora/LDC97S62/swb1_d*/data/ -name "sw0${file_number}.sph"`
  # discard utterances shorter than 30 ms since Kaldi pitch feats are computed on 25 ms windows
  if (( "$diff" > 2 ))
  then
    echo "$file_name ../../../tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 1 -t $start_sec:$end_sec $sph |" >> audio/helpers/wav.scp
    if [ "$channel" == "A" ]
    then
      echo "Processing file: "$file_name "channel: "$channel
      ../../../tools/sph2pipe_v2.5/sph2pipe -f wav -c 1 -t $start_sec:$end_sec $sph audio/wav/$file_name.wav
    else
      echo "Processing file: "$file_name "channel: "$channel
      ../../../tools/sph2pipe_v2.5/sph2pipe -f wav -c 2 -t $start_sec:$end_sec $sph audio/wav/$file_name.wav
    fi
  else
    echo "$file_name" >> audio/helpers/utts_zero_dur
  fi
done

