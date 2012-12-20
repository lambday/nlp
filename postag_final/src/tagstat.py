#!/usr/bin/env python
# This script takes the tag-wise stats and output
# overall tag-wise accurary

import sys
from bnc import tagset, tagdictionary

if len(sys.argv) < 3:
	print 'Usage:',sys.argv[0],'<stat-file-basename> <number-of-files>'
	sys.exit(1)

stat = [0.0] * len(tagset)
for i in range( int(sys.argv[2]) ):
	try:
		s = open( sys.argv[1] + str(i) + ".txt", "r" )
		stat = map(lambda x:x[0]+x[1],zip(stat,map(lambda x:float(x.split(" ")[1]),s.read().strip().split("\n"))))
		s.close()
	except IOError:
		print sys.argv[0],'couldn\'t read the input file',sys.argv[1],i,'.txt'
		sys.exit(2)
stat = map(lambda x:x/int(sys.argv[2]),stat)

try:
	s = open( sys.argv[1] + ".txt", "w" )
	for i in range(len(tagset)):
		s.write(tagset[i] + " " + str(stat[i]) + "\n" )
	s.close()
except IOError:
	print sys.argv[0],'something went wrong'
	sys.exit(3)
