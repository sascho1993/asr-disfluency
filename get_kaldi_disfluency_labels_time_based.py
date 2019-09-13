"""
Disfluency labels for Kaldi output are generated based on time overlap with silver disfluency labels.
Words are split into time frames of 10 ms. Each time frame is assigned a disfluency label depending on 
what label the corresponding time frame has based on MS-State time stamps.
If the time frame lies between two word boundaries in MS-State, the frame gets a double-label, e.g.:
  MS-State:      IP IP IP IP X    X    X    X    X    X    C C C C
  Kaldi word:       W  W  W  W    W    W    W    W    W    W
  Kaldi label:      IP IP IP IP-C IP-C IP-C IP-C IP-C IP-C C
  where X is a frame between two words, W is one frame in the Kaldi word, and IP-C is a double-label.

For each Kaldi word, the frame values are added up, while a double-label counts as half a label each,
i.e. IP-C counts as 0.5*IP and 0.5*C.
  -> 6 * IP
     4 * C
The label which is assigned most often to a Kaldi word is then chosen as its disfluency label.
"""

import sys

kaldi_output = sys.stdin
silver_file = open("data/silver_wd/ms_silver_for_kaldi", "r")

utt_start_times = {}
silver = {}
for line in silver_file:
    try:
        utt_id, file_id, token, disfluency, start, end = line.split()
        if utt_id not in silver:
            silver[utt_id] = [[],[],[],[]]
            prev_end = None
            prev_disfluency = None
            utt_start_times[utt_id] = start
        start = int(start)
        end = int(end)
        dur = end-start
        # Variety to add Filler word information; not used in current system
        #if token in ['uh', 'um', 'hm'] and disfluency == "O":
        #    disfluency = 'FIL_O'
        #elif token in ['uh', 'um', 'hm'] and disfluency == "C":
        #    disfluency = 'FIL_C'
        if prev_end != None and prev_disfluency != None:
            pause_len = start - prev_end
            # pause disfluency labels are a combination of last and next disfluency label, e.g. BE_IP-C
            if prev_disfluency != disfluency:
                pause_disfl = prev_disfluency + "-" + disfluency
            else:
                pause_disfl = disfluency
            if pause_len > 0:
                silver[utt_id][0].append("PAU")
                silver[utt_id][1].append(prev_end)
                silver[utt_id][2].append(start)
                silver[utt_id][3].extend([pause_disfl]*pause_len)
        silver[utt_id][0].append(token)
        silver[utt_id][1].append(start)
        silver[utt_id][2].append(end)
        silver[utt_id][3].extend([disfluency]*dur)
        prev_end = end
        prev_disfluency = disfluency
    except:
        pass

prev_utt_id = ""
for line in kaldi_output:
    utt_id, channel, start, dur, token = line.split()
    token = token.strip()
    if prev_utt_id != "" and utt_id != prev_utt_id:
        print ""
        #pass
    # skip [noise] etc.
    if token.strip("[]") == token:
        start = int(round(float(start)*100))
        dur = int(round(float(dur)*100))
        if utt_id != prev_utt_id:
            sentence_start = int(utt_start_times[utt_id])
        token_start = start - sentence_start
        token_end = token_start + dur
        disfluency_tags = silver[utt_id][3][token_start:token_end]
        tags = ["O", "BE", "IE", "IP", "BE_IP", "C_IE", "C_IP", "C"]
        tag_scores = [0.0] * 8
        for tag in disfluency_tags:
            if tag in tags:
                tag_index = tags.index(tag)
                tag_scores[tag_index] += 1
            else:
                tag_prev, tag_next = tag.split("-")
                tag_index = tags.index(tag_prev)
                tag_scores[tag_index] += 0.5
                tag_index = tags.index(tag_next)
                tag_scores[tag_index] += 0.5
        most_probable_tag = tag_scores.index(max(tag_scores))
        disfluency_tag = tags[most_probable_tag]
        # sw2638A_utt_069	sw2638A	everybody	O	-1	29
        # Don't know why Kaldi starts a frame earlier, shouldn't be possible..
        if token_start == -1:
            token_start = 0
        print utt_id + '\t' + utt_id[0:7] + '\t' + token + '\t' + disfluency_tag + '\t' + str(token_start) + '\t' + str(token_end)
        #if utt_id == 'sw4940B_utt_069':
        #    print utt_id + '\t' + token + '\t' + str(sentence_start) + '\t' + str(start)  + '\t' + str(token_start)  + '\t' + str(token_end)  + '\t' + str(dur)
        prev_utt_id  = utt_id
            




