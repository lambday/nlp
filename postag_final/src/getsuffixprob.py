#!/usr/bin/env python

import sys
from re import search
from bnc import tagset, tagdictionary, getcounts, BST, BSW, isEndSentence, suffix
from util import convertIfNeeded
from os import listdir
from os.path import isfile, join

# Utility functions
# -----------------

# INPUT : Takes one string and one list of tuples, [(tagindex,count)]
# OUTPUT : Nothing
# JOB : Increates the count in suffix probability table
def spTableCount( word, curtagi ):
	for i in curtagi:
		for s in suffix:
			if search(s+"$",word) != None:
				suffixProbTable[i[0]][suffix.index(s)] += 1
				break

# Main script begins
# ------------------

if (len(sys.argv) < 3):
	print 'Usage:', sys.argv[0], '<corpus-dir> <suffix-file>'
	sys.exit(1)

# Read the corpus directory and put the filenames in corpusFiles
try:
        corpusFiles = [ f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1],f)) ]
except OSError:
        print sys.argv[0],'the corpus directory doesn\'t exist'
        sys.exit(2)

# Check if the corpus directory is empty
if len(corpusFiles) == 0:
        print sys.argv[0],'Corpus directory is empty'
        sys.exit(3)

# Create an empty suffix table, len(tagset) \times len(suffix)
suffixProbTable = []
for i in range(len(tagset)):
	suffixProbTable.append([0] * len(suffix))

# Begin-sentence tagindex list to be used later
# For its meaning, refer to the description of 'curtagi'
bstagi = [(BST,1.0)]

# Go through each of the corpus files and gather the counts
for corpus in corpusFiles:
        try:
                c = open( join(sys.argv[1],corpus), "r" )
        except IOError:
                print sys.argv[0],'Error: Couldn\'t read corpus file',corpus
                continue
        # Split for each word_tag combination and create a list
        curCorpus = c.read().strip().split(" ")
        # Close the file
        c.close()

	# For the first tag_word, we consider this as begin sentence tag_word
	bstag = curCorpus[0].split("_")[0]
	bsword = convertIfNeeded(curCorpus[0].split("_")[1],bstag)

	# Get the tag-id(s) with the count(s) to be added
	# Description: curtagi (Current Tag Index) is a list of
	# tuples, (tagindex, count), where tagindex is the corresponding
	# tagindex in tagset, and count is the count to be added for that
	# tag, which is 1 for normal tags and 0.5 for ambiguous tags
	curtagi = getcounts( bstag )

	# Suffix probability count
	spTableCount( bsword, curtagi )
	
	# Iterate over the corpus for gathering counts
	for i in range(len(curCorpus))[1:]:
		# Get the current tag_word
		curtag = curCorpus[i].split("_")[0]
		curword = convertIfNeeded(curCorpus[i].split("_")[1],curtag)

		# Get the tag-id(s) with the count(s) to be added
		# Description: curtagi (Current Tag Index) is a list of
		# tuples, (tagindex, count), where tagindex is the corresponding
		# tagindex in tagset, and count is the count to be added for that
		# tag, which is 1 for normal tags and 0.5 for ambiguous tags
		curtagi = getcounts( curtag )
		
		# Suffix probability count
		spTableCount( curword, curtagi )

# Normalize the suffix probability table (uses ADD-ONE smoothing)
suffixProbTable = map(lambda row:map(lambda x:(1+float(x))/(1+sum(row)),row),suffixProbTable)

# Open trigram-transition table file for writing
try:
	stmp = open( sys.argv[2], "w" )
except IOError:
	print sys.argv[0],'Couldn\'t open',sys.argv[2],'for writing'
	sys.exit(5)

# Store the suffix probability table
# FORMAT: len(tagset) \times len(suffix) matrix, comma separated
for row in suffixProbTable:
	for val in row:
		stmp.write( str(val) + " ")
	stmp.write( "\n" )
