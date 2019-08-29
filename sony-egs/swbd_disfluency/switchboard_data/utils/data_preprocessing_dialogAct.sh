#!/bin/bash

# Get paths of all transcripts:
ls /speech/db/SpeechCorpora/LDC97S62/switchboard-I-data/swb1_dialogact_annot/*/* | grep "\.utt" > data/raw_text/utts_abs_path

# Generate dialog files after first clean up:
mkdir -p data/raw_text/first_cleanup
cat data/raw_text/utts_abs_path | while read file
do
  file_name=`echo $file | awk -F '/' '{print $9}'`
  number=`cat $file | grep -n $"==============\+" | tr -d ":" | tr -d "="`
  l_number=$((number + 1))
  file_name_a=`echo $file_name`"_A"
  file_name_b=`echo $file_name`"_B"
  tail -n+$l_number $file | sed '/^$/d' | awk -F ' ' '{$1=""; print $0}' | grep "A.[0-9]" > data/raw_text/first_cleanup/$file_name_a
  tail -n+$l_number $file | sed '/^$/d' | awk -F ' ' '{$1=""; print $0}' | grep "B.[0-9]" > data/raw_text/first_cleanup/$file_name_b
done

# Add file-id at every line
mkdir -p data/raw_text/second_cleanup
for file in data/raw_text/first_cleanup/*
do
  f_name=`echo $file | sed 's/text\/first_cleanup\/sw_[0-9][0-9][0-9][0-9]_//g' | sed 's/.utt_[AB]//g'`
  speaker=`echo $file | sed 's/text\/first_cleanup\/sw_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9].utt_//g'`
  file_name=`echo $file | sed 's/text\/first_cleanup\///g'`
  fileid=$f_name$speaker
  cat $file | while read line
  do
    echo -e 'sw'$fileid' '$line >> data/raw_text/second_cleanup/$file_name
  done
done

cat data/raw_text/second_cleanup/* > data/raw_text/all_utts

rm -rf data/raw_text/first_cleanup
rm -rf data/raw_text/second_cleanup

