# encode markers F (filled pause), D (Discourse marker), E (Edit word)
# as binary values and a column reserved for each of them: F\tD\tE

import sys

f = open(sys.argv[1], "r")
out = open(sys.argv[2], "w")

for line in f:
    line = line.split('\t')
    remain = ""
    m = ""
    try:
        remain = "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(line[0],line[1],line[2],line[3],line[4],line[5], line[6])
        marker = line[7].strip()
        if marker == "" or marker == "C":
            m = "\t0\t0\t0"
        elif marker == "F":
            m = "\t1\t0\t0"
        elif marker == "D":
            m = "\t0\t1\t0"
        elif marker == "E":
            m = "\t0\t0\t1"
        else:
            print (line)
    except:
        pass
    res = remain + m
    out.write("{}\n".format(res))
    

