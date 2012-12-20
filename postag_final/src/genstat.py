#!/usr/bin/env python
# This script takes the confusion matrix as input and outputs
# overall accuracy and tag-wise accurary

import sys
from bnc import tagset, tagdictionary

if len(sys.argv) < 3:
	print 'Usage:',sys.argv[0],'<confusion-matrix> <stat-file>'
	sys.exit(1)

try:
	cnf = open( sys.argv[1], "r" )
except IOError:
	print sys.argv[0],'couldn\'t read the input file',sys.argv[1]
	sys.exit(2)

try:
	stat = open( sys.argv[2], "w" )
except IOError:
	print sys.argv[0],'couldn\'t read the input file',sys.argv[2]
	sys.exit(3)

# read the confusion matrix as float 2d matrix
confusionMatrix = []
for line in cnf:
	confusionMatrix.append(map(lambda x: int(x),line.strip().split(",")[:-1]))

totalcorrect = 0
total = 0

for i in range(len(tagset)):
	correct = confusionMatrix[i][i]
	incorrect = sum(confusionMatrix[i]) - correct
	try:
		stat.write(tagset[i] + " " + str(float(correct) * 100 /sum(confusionMatrix[i])) + "\n" )
	except ZeroDivisionError:
		stat.write(tagset[i] + " " + str(0.0) + "\n" )
	totalcorrect += correct
	total += sum(confusionMatrix[i])

print str(float(totalcorrect) * 100 /total)

stat.close()
cnf.close()
