#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary

if len(sys.argv) < 3:
	print 'Usage:',sys.argv[0],'<confusion-matrix> <stat-file>'
	sys.exit(1)

try:
	cnf = open( sys.argv[1], "r" )
except IOError:
	print sys.argv[0],'couldn\'t read the input files'
	sys.exit(2)

try:
	stat = open( sys.argv[2], "w" )
except IOError:
	sys.exit(3)

# read the transition table as float 2d matrix
confusionMatrix = []
for line in cnf:
	confusionMatrix.append(map(lambda x: int(x),line.strip().split(",")[:-1]))

for i in range(len(tagset)):
	correct = confusionMatrix[i][i]
	incorrect = sum(confusionMatrix[i]) - correct
	stat.write(str(correct) + " " + str(incorrect) + "\n")

stat.close()
cnf.close()
