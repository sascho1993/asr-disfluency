dir=$1

mkdir -p $dir

cat /speech/db/SpeechCorpora/LDC97S62/transcriptions/swb_ms98_transcriptions/*/*/sw*-ms98-a-word.text > $dir/all_ms_words



# (1a) Transcriptions preparation
# make basic transcription file (add segments info)
# **NOTE: In the default Kaldi recipe, everything is made uppercase, while we 
# make everything lowercase here. This is because we will be using SRILM which
# can optionally make everything lowercase (but not uppercase) when mapping 
# LM vocabs.
awk '{ 
       name=substr($1,1,6); side=substr($1,7,1); 
       stime=$2; etime=$3;
       printf("%s%s_%06.0f-%06.0f", 
              name, side, int(100*stime+0.5), int(100*etime+0.5));
       for(i=4;i<=NF;i++) printf(" %s", $i); printf "\n"
}' $dir/all_ms_words  > $dir/ms_words1


# Remove SILENCE, <B_ASIDE> and <E_ASIDE>.

# Note: we have [NOISE], [VOCALIZED-NOISE], [LAUGHTER], [SILENCE].
# removing [SILENCE], and the <B_ASIDE> and <E_ASIDE> markers that mark
# speech to somone; we will give phones to the other three (NSN, SPN, LAU). 
# There will also be a silence phone, SIL.
# **NOTE: modified the pattern matches to make them case insensitive
cat $dir/ms_words1 \
  | perl -ane 's:\s\[SILENCE\](\s|$):$1:gi; 
               s:\s\[NOISE\](\s|$):$1:gi;
               s:\s\[LAUGHTER\](\s|$):$1:gi;
               s:\s\[VOCALIZED-NOISE\](\s|$):$1:gi;
               s/<B_ASIDE>//gi; 
               s/<E_ASIDE>//gi; 
               print;' \
  | awk '{if(NF > 1) { print; } } ' > $dir/ms_words2


# **NOTE: swbd1_map_words.pl has been modified to make the pattern matches 
# case insensitive
local/swbd1_map_words.pl -f 2- $dir/ms_words2  > $dir/words



# format acronyms in text
python local/map_acronyms_transcripts.py -i $dir/words -o $dir/words_map \
  -M local/acronyms.map

awk '{ 
       name=substr($1,1,7); stime=substr($1,9,6); etime=substr($1,16,6);
       token=$2;
       printf("%s\t%s\t%s\t%s", 
              name, token, stime, etime);
       for(i=4;i<=NF;i++) printf(" %s", $i); printf "\n"
}' $dir/words_map  > $dir/words

