cat data/raw_text/all_utts_man | sed 's/@A/A/g' | sed 's/@B/B/g' | sed 's/{/{ /g' | sed 's/  / /g' | sed 's/{ A /{A /g' | sed 's/{ C /{C /g' | sed 's/{ D /{D /g' | sed 's/{ E /{E /g' | sed 's/{ F /{F /g' | sed 's/}/ } /g' | sed 's/\[/[ /g' | sed 's/#/ # /g' | sed 's/((/(( /g' | sed 's/))/ ))/g' | sed 's/\*\[ \[/*[[/g' | sed 's/\*\[\[/ *[[/g' | sed 's/\]/ ]/g' | sed 's/\] \]/]]/g' | sed 's/+ \]/+]/g' | sed 's/<</<< /g' | sed 's/<+/<+ /g' | sed 's/\// \//g' | sed 's/< \//<\//g' | sed 's/  / /g' | sed 's/- \//-\//g' | sed 's/--//g' | sed 's/((//g' | sed 's/))//g' | sed 's/#//g' | sed 's/+>/ +>/g' | sed 's/--/ -- /g' | sed 's/>>/ >>/g' | sed 's/ , / /g' | sed 's/  / /g' > data/raw_text/all_utts_clean


# split apostrophes
cat data/raw_text/all_utts_clean | sed "s/n't/ n't/g" | sed "s/'s/ 's/g" | sed "s/'ll/ 'll/g" | sed "s/'re/ 're/g" | sed "s/'ve/ 've/g" | sed "s/'m/ 'm/g" | sed "s/'d/ 'd/g" > data/raw_text/all_utts_clean_apos
