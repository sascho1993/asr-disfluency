import sys

f = open(sys.argv[1], "r")

start_time = ""
for line in f:
    try:
        file_id, file_name, word, tag, start, end = line.split()
        end = int(end.strip())
        start = int(start)
        if start_time == "":
            start_time = start
    except:
        if start_time != end:
            print file_id, '\t', start_time, '\t', end
        start_time = ""
