#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary

if len(sys.argv) < 2:
	print 'Usage',sys.argv[0],'<results-logfile>'
	sys.exit(1)

try:
	f = open( sys.argv[1], "r" )
	total = []
	for line in f:
		total.append(line.strip().split(" ")[0])
	try:
		print sum(map(lambda x:float(x),total))/len(total)
	except ZeroDivisionError:
		print sys.argv[0],'log-file empty'
		sys.exit(2)
	f.close()
except IOError:
	print sys.argv[0],'cannot open results-log file'
	sys.exit(3)
