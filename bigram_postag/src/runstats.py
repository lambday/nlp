#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary
from os import listdir
from os.path import isfile, join

if len(sys.argv) < 3:
	print 'Usage',sys.argv[0],'<globstats-directory> <globstats-file>'
	sys.exit(1)
try:
        statfiles = [ f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1],f)) ]
except OSError:
        print sys.argv[0],'the globstats-directory doesn\'t exist'
        sys.exit(2)

avgstat = [0.0] * len(tagset)

for statfile in statfiles:
	try:
		f = open( sys.argv[1] + "/" + statfile, "r" )
		curstat = []
		for line in f:
			curstat.append(line.strip().split(",")[1])
		avgstat = map(lambda x:x[0]+x[1],zip(avgstat,map(lambda x:float(x),curstat)))
		f.close()
	except IOError:
		print sys.argv[0],'cannot open globstat file'
		sys.exit(3)
avgstat = map( lambda x: x/len(statfiles),avgstat )

# write tag-wise statistics
try:
        s = open( sys.argv[2], "w" )
        for i in range(len(tagset)):
                s.write( tagset[i] + "," +  str(avgstat[i]) + "\n" )
except IOError:
        print sys.argv[0],'couldn\'t write the avg stat file'
