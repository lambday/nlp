#!/usr/bin/env python
#####################
# This script stores zeros in a transition table file

import sys
from bnc import tagset

fname = "tran.tmp"
if (len(sys.argv) < 2):
	print 'Temp filename not specified, default as tran.tmp'
else:
	fname = sys.argv[1]
# open the file for storing transition table
try:
	tmp = open( fname, "w" )
except IOError:
	sys.exit(1)

# define the transition table as 2d matrix
transitionTable = []
for i in range(len(tagset) + 1): # one extra row for the begin-sentence tag
        transitionTable.append([0] * len(tagset))

# store the transition table
for row in transitionTable:
        for val in row:
                tmp.write(str(val)+" ")
	tmp.write("\n")
