#!/usr/bin/env python
# combines all the confusion matrices in the given directory into one
# and stores in the results directory with iteration number

import sys
from bnc import tagset, tagdictionary
from os import listdir
from os.path import isfile, join

if len(sys.argv) < 3:
        print 'Usage:',sys.argv[0],'<results-directory> <iteration-number>'
        sys.exit(1)

try:
	dirname = sys.argv[1]	#+"/result"+sys.argv[2]+"/cnf/"
        cnffiles = [ f for f in listdir(dirname) if isfile(join(dirname,f)) ]
	cnffiles = filter( lambda x: x.split(".")[-1] == "csv" and x or None ,cnffiles)
except OSError:
        print sys.argv[0],'the confusion-matrix directory doesn\'t exist'
        sys.exit(2)

# create the merged confusion matrix
mergedMatrix = []
for i in range(len(tagset)):
	mergedMatrix.append( [0] * len(tagset) )

# read all the stat-files and calculate global stat
for cnf in cnffiles:
        try:
                f = open( join(dirname,cnf), "r" )
		# read the transition table as float 2d matrix
		confusionMatrix = []
		for line in f:
			confusionMatrix.append(map(lambda x: int(x),line.strip().split(",")[:-1]))
		# merge this with the overall confusion matrix
		for i in range(len(tagset)):
			mergedMatrix[i] = map( lambda x: x[0] + x[1], zip(mergedMatrix[i], confusionMatrix[i]))
        except IOError:
                print sys.argv[0],'Error reading csv file', cnf

# print the merged confusion matrix in a file
name = "conf_run"+ sys.argv[2] +".csv"
cnf = open( name, "w" )
for i in range(len(tagset)):
        for j in range(len(tagset)):
                cnf.write(str(mergedMatrix[i][j])+",")
        cnf.write("\n")
