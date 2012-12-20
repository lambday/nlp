#!/usr/bin/env python
#####################
# This script takes the transition table and emission table and calculates
# the transition probabilities, emission probabilities

import sys
from bnc import tagset, tagdictionary

if (len(sys.argv) < 3):
        print 'Usage:', sys.argv[0], '<transition-filename> <emission-filename'
        sys.exit(1)
try:
        ttmp = open( sys.argv[1], "r" )
	etmp = open( sys.argv[2], "r" )
except IOError:
        print 'Error: (', sys.argv[0], ') Input file doesn\'t exist'
        sys.exit(2)

# read the transition table as float 2d matrix
transitionTable = []
for line in ttmp:
        transitionTable.append(map(lambda x: float(x),line.strip().split(" ")))

# read the emission table as a dictionary
emissionTable={}
for line in etmp:
	arr = line.strip().split(" ")
	emissionTable[arr[0]] = map( lambda x: float(x), arr[1:] )

# close the tmp file and open for writing
try:
        ttmp.close()
        etmp.close()
        ttmp = open( sys.argv[1], "w" )
        etmp = open( sys.argv[2], "w" )
except IOError:
        sys.exit(3)

# normalize the transition table to get the probability
transProbTable = []
for row in transitionTable:
	try:
		transProbTable.append(map(lambda x: float(x)/sum(row), row))
	except ZeroDivisionError:
		transProbTable.append(map(lambda x: float(x),row))

# store the transition probability table
for row in transProbTable:
        for val in row:
                ttmp.write(str(val)+" ")
        ttmp.write("\n")

# normalize the emission table to get the probability
emissionProbTable = {}
for word, row in emissionTable.items():
	try:
		emissionProbTable[word] = map(lambda x: float(x)/sum(row), row)
	except ZeroDivisionError:
		emissionProbTable[word] = map(lambda x: float(x), row)

# store the emission probability table
for word, row in emissionProbTable.items():
        etmp.write(word + " ")
        for val in row:
                etmp.write(str(val)+" ")
        etmp.write("\n")
