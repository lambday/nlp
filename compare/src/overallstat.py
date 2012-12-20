#!/usr/bin/env python

import sys

if len(sys.argv) < 2:
	print 'Usage',sys.argv[0],'<log-file>'
	sys.exit(1)

# Go through the log file and gather the print the avg stat
try:
	f = open( sys.argv[1], "r" )
	total = []
	for line in f:
		total.append(line.strip().split(" ")[0])
	try:
		print sum(map(lambda x:float(x),total))/len(total)
	except ZeroDivisionError:
		sys.exit(2)
	f.close()
except IOError:
	print sys.argv[0],'cannot open results-log file',sys.argv[1]
	sys.exit(3)
