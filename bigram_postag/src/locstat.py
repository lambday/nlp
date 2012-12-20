#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary
from os import listdir
from os.path import isfile, join

if len(sys.argv) < 2:
	print 'Usage:',sys.argv[0],'<stat-file-directory>'
	sys.exit(1)
try:
	statfiles = [ f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1],f)) ]
	statfiles = filter( lambda x: x.split(".")[0].split("_")[-1] == "stat" and x or None ,statfiles)
except OSError:
	print sys.argv[0],'the stat-file directory doesn\'t exist'
	sys.exit(2)

# create the output vector containing the counts
count = []
for i in range(len(tagset)):
	count.append( [0]* 2 )

# read all the stat-files and calculate global stat
for statfile in statfiles:
	try:
		f = open( sys.argv[1] + "/" + statfile, "r" )
		i = 0
		for line in f:
			stat = map(lambda x: int(x),line.strip().split(" "))
			count[i][0] += stat[0]
			count[i][1] += stat[1]
			i += 1
	except IOError:
		print sys.argv[0],'Error reading stat file'

# write tag-wise statistics
try:
	globstat = open( "locstat.csv", "w" )
	for i in range(len(tagset)):
		try:
			percent = float(count[i][0]) / float(sum(count[i])) * 100.0
		except ZeroDivisionError:
			percent = 0.0
		globstat.write( tagset[i] + "," +  str(percent) + "\n" )
except IOError:
	print sys.argv[0],'couldn\'t write the global stat file'

# print overall performance
c = zip(*count)
percent = float(sum(c[0])) / float(sum(c[0]) + sum(c[1])) * 100.0
print percent, '% tags are correct'
