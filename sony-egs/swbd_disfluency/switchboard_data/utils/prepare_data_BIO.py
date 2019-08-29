#!/usr/bin/env python
"""
The dialogAct corpus is taken as an input token by token.

"""
import re

utts = open("data/raw_text/all_utts_clean_apos","r")
out = open("data/labeled/switchboard_prepared_BIO", "w")

# true if word == '{', false if word == '}'
brace_comment = False
brace_comment_next = False
# true if word == '{D', false if word == '}' and discourse == True
discourse = False
discourse_next = False
# true if word == '{E', false if word == '}' and edit == True
edit = False
edit_next = False
# true if word == '{F', false if word == '}' and filled_pause == True
filled_pause = False
filled_pause_next = False
# true if word == '{C', false if word == '}' and coordinate == True
coordinate = False
coordinate_next = False
# true if word == '{A', false if word == '}' and aside == True
aside = False
aside_next = False

# true if word == '*[[', false if word == ']]' and ignore_ast == True
ignore_ast = False
# true if word == '<+', false if word == '+>' and ignore_plus_comment == True
ignore_plus_comment = False
# true if word == '<<', false if word == '>>' and ignore_noise == True
ignore_noise = False

reparandum = False
repair = False
beginning_edit = False
ip = False

# Count number of open brackets and number of pluses, they both get decreased when ']' is encountered.
# Both counts have to be zero again when beginning a new file
count = 0
plus_count = 0

ignore = ["-", "--", "#", "(("]
# slash units
su = ["-/", "/"]
# set to true to output a new line after each slash unit
split_sentence = True

bracket_open = 0
bracket_close = 0
# count words in sentence to enumerate them in output, each sentence starts with 1
word_number = 0
rm_count = 0
rr_count = 0
rm_rr_count = 0
prev_file_id = ""
prev_prev_file_id = ""
prev_utt_number = ""
prev_speaker_turn = ""

first_word = True

for line in utts:
    file_id,utt = line.split(" ",1) 
    utt = utt.strip().split(" ")
    speaker_turn = utt[0]
    utt_number = utt[1]
    # bracket is not closed until the end of the file
    if prev_prev_file_id != "" and prev_prev_file_id != prev_file_id and count != 0:
        print "Error: count is not zero.\t\t{}\t{}\t{}".format(prev_prev_file_id, prev_file_id, count)
    # too many pluses or too little brackets in file
    if prev_prev_file_id != "" and prev_prev_file_id != prev_file_id and plus_count != 0:
        print "Error: plus count is not zero.\t\t{}\t{}\t{}".format(prev_prev_file_id, prev_file_id, plus_count)
    # word count must be 0 at end of a file
    if prev_prev_file_id != "" and prev_prev_file_id != prev_file_id and word_number != 0:
        print "Error: word_number is not zero in new file.\t\t{}\t{}\t{}".format(prev_prev_file_id, prev_file_id, word_number)
    for word in utt[2:]:
        word = word.strip(".,?! \n\"")
        # The script works with two words at each time step. Skip the first word.
        if first_word == True:
            prev_word = word
            first_word = False
        elif prev_word in ignore:
            prev_word = word
        elif prev_word in su:
            if split_sentence == True:
                word_number = 0
                out.write("\n")
                prev_word = word
            else:
                prev_word = word
        elif re.match('<(/?[A-Z]*[a-z]*_?\-?[a-z]*\.?)+>', prev_word):
            prev_word = word
        #markers open
        elif prev_word == "{D":
            discourse = True
            prev_word = word
        elif prev_word == "{E":
            edit = True
            prev_word = word
        elif prev_word == "{F":
            filled_pause = True
            prev_word = word
        elif prev_word == "{C":
            coordinate = True
            prev_word = word
        elif prev_word == "{A":
            aside = True
            prev_word = word
        elif word == "{":
            brace_comment = True
        # comments like *[[ slash error ]]
        elif prev_word == "*[[":
            ignore_ast = True
            prev_word = word
        elif ignore_ast == True and prev_word != "]]":
            prev_word = word
        elif ignore_ast == True and prev_word == "]]":
            ignore_ast = False
            prev_word = word
        elif re.match('\]\].*', prev_word) and ignore_ast == False:
            print "Error: ignore_ast is already False.\t\tfile_id: {}\tspeaker_turn: {}".format(prev_file_id, speaker_turn)
            prev_word = word
        # comments like << faint >>
        elif prev_word == "<<":
            ignore_noise = True
            prev_word = word
        elif prev_word == ">>":
            ignore_noise = False
            prev_word = word
        elif ignore_noise == True:
            prev_word = word
        # comments like <+ What to do about x +>
        elif prev_word == "<+":
            ignore_plus_comment = True
            prev_word = word
        elif prev_word == "+>":
            ignore_plus_comment = False
            prev_word = word
        elif ignore_plus_comment == True:
            prev_word = word
        # disfluencies open
        elif prev_word == "[":
            reparandum = True
            count += 1
            bracket_open += 1
            if repair == False:
                beginning_edit = True
            prev_word = word
        elif prev_word == "+" and count > 1:
            repair = True
            plus_count += 1
            if count == plus_count:
                reparandum = False
            prev_word = word
        elif prev_word == "+" and count == 1:
            repair = True
            reparandum = False
            plus_count += 1
            prev_word = word
        elif prev_word == "+" and count == 0:
            print "Error: count is 0 when encountering +.\t\tfile_id: {}\tspeaker_turn: {}".format(file_id, speaker_turn)
            prev_word = word
        # disfluencies close
        elif prev_word == "]" and count > 1:
            count -= 1
            plus_count -= 1
            bracket_close += 1
            if count != plus_count:
                repair = False
            else:
                repair = True
            prev_word = word
        elif prev_word == "]" and count == 1:
            count -= 1
            plus_count -= 1
            repair = False
            bracket_close += 1
            prev_word = word
        elif prev_word == "]" and count == 0:
            print "Error: word is ] when count is already 0.\t\tfile_id: {}\tspeaker_turn: {}".format(file_id, speaker_turn)
            prev_word = word
        elif prev_word == "+]" and count == 1:
            count -= 1
            reparandum = False
            bracket_close += 1
            prev_word = word
        elif prev_word == "+]" and count == 0:
            print "Error: word is +] when count is already 0\t\tfile_id: {}\tspeaker_turn: {}".format(file_id, speaker_turn)
            prev_word = word
        elif prev_word == "+]" and count > 1:
            count -= 1
            bracket_close += 1
            if count == plus_count:
                reparandum = False
            prev_word = word
            # check which attributes the word has
        elif prev_word != "":
            if discourse + edit + filled_pause + coordinate > 1:
                print "Error: more than one marker is activated.\t\t{} {}\t{}\t{}".format(prev_file_id, prev_speaker_turn, prev_utt_number, prev_word)
                prev_word = word
            # skip } as a word to be investigated in order to make BE_IP detectable:
            # [ {C and } + {C and } ]
            elif word == "))":
                pass
            elif word == "}":
                if discourse == True:
                    discourse_next = True
                elif edit == True:
                    edit_next = True
                elif filled_pause == True:
                    filled_pause_next = True
                elif coordinate == True:
                    coordinate_next = True
                elif aside == True:
                    aside_next = True
                elif brace_comment == True:
                    brace_comment_next = True
                else:
                    print "Error: marker closed when none was open.\t\tfile_id: {}\tspeaker_turn: {}".format(prev_file_id, speaker_turn)
            else:
                word_number += 1
                marker = "D"*discourse + "E"*edit + "F"*filled_pause + "C"*coordinate
                rm = int(reparandum == True)
                rr = int(repair == True)
                if plus_count > count:
                    print "Error: plus_count > count\t\tfile_id: {}\tspeaker_turn: {}".format(file_id,speaker_turn)
                if bracket_open < bracket_close:
                    print "Error: bracket_open < bracket_close\t\tfile_id: {}\tspeaker_turn: {}".format(file_id,speaker_turn)
                if discourse_next == True:
                    discourse_next = False
                    discourse = False
                elif edit_next == True:
                    edit_next = False
                    edit = False
                elif filled_pause_next == True:
                    filled_pause_next = False
                    filled_pause = False
                elif coordinate_next == True:
                    coordinate_next = False
                    coordinate = False
                elif aside_next == True:
                    aside_next = False
                    aside = False
                elif brace_comment_next == True:
                    brace_comment_next = False
                    brace_comment = False
                    continue
                # flags are turned into BIO tags
                if reparandum == False and repair == False:
                    edit_type = "O"
                else:
                    if beginning_edit == True:
                        beginning_edit = False
                        if reparandum == True and repair != True:
                            if word == "+" or word == "+]":
                                edit_type = "BE_IP"
                            else:
                                edit_type = "BE"
                        elif reparandum == True and repair == True:
                            edit_type = "C_IE"
                        elif repair == True:
                            print "Error: only repair at edit beginning"
                    else:
                        if word == "+" or word == "+]":
                            if reparandum == True and repair == False:
                                edit_type = "IP"
                            elif reparandum == True and repair == True:
                                edit_type = "C_IP"
                        else:
                            if reparandum == True and repair == False:
                                edit_type = "IE"
                            elif reparandum == True and repair == True:
                                if word == "]":
                                    edit_type = "C_IP"
                                else:
                                    edit_type = "C_IE"
                            elif repair == True:
                                edit_type = "C"
                
                out.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(str(word_number), prev_file_id, prev_speaker_turn, prev_utt_number, prev_word.lower(), edit_type, marker))
                prev_word = word
        else:
            prev_word = word
        prev_prev_file_id = prev_file_id
        prev_file_id = file_id
        prev_utt_number = utt_number
        prev_speaker_turn = speaker_turn
utts.close()
out.close()
