#!/usr/bin/env python
##############################################################################
# This script calculates the probability values $P(S_{k})$, $P(S_{k}|S_{k-1})$
# and $P(S_{k}|S_{k-1},S_{k-2})$. It gathers the counts in unigram-tag-
# -transition-table (utTable), bigram-tag-transition-table (btTable) and 
# trigram-tag-transition-table (ttTable). 
# It also calculates the emission probability P(O_{k}|S_{k}).
#############################################################################

import sys
from bnc import tagset, tagdictionary, getcounts, BST, BSW, isEndSentence
from util import convertIfNeeded
from os import listdir
from os.path import isfile, join

# Utility functions
# -----------------

# INPUT : Takes one list of tuples, [(tagindex,count)]
# OUTPUT : Nothing
# JOB : Increates the count in unigram tag transition table
#def utTableCount( curtagi ):
#	for i in curtagi:
#		# i is (tagindex, count)
#		utTable[i[0]] += i[1]

# INPUT : Takes two list of tuples, [(tagindex,count)]
# OUTPUT : Nothing
# JOB : Increates the count in bigram tag transition table
def btTableCount( prevtagi_1, curtagi ):
	for i in curtagi:
		for j in prevtagi_1:
			# i and j are (tagindex, count)
			btTable[j[0]][i[0]] += j[1] * i[1]

# INPUT : Takes three list of tuples, [(tagindex,count)]
# OUTPUT : Nothing
# JOB : Increates the count in trigram tag transition table
#def ttTableCount( prevtagi_2, prevtagi_1, curtagi ):
#	for i in curtagi:
#		for j in prevtagi_1:
#			for k in prevtagi_2:
#				# i, j and k are (tagindex, count)
#				ttTable[k[0]][j[0]][i[0]] += k[1] * j[1] * i[1]

# INPUT : Takes one string and one list of tuples, [(tagindex,count)]
# OUTPUT : Nothing
# JOB : Increates the count in emission probability table
#def epTableCount( word, curtagi ):
#	for i in curtagi:
#		if word in emissionTable[i[0]]:
#			emissionTable[i[0]][word] += i[1]
#		else:   # New word found
#			emissionTable[i[0]][word] = i[1]
	
# Main script begins
# ------------------

if (len(sys.argv) < 3):
	print 'Usage:', sys.argv[0], '<corpus-dir> <bigram-file>'
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

# Initialize the unigram-tag-transition table as list
# utTable[S_{i}] format
#utTable = [0.0] * len(tagset)

# Initialize the bigram-tag-transition table as 2D matrix
# btTable[S_{i-1}][S_{i}] format
btTable = []
for i in range(len(tagset) + 1): 	
# The last row for the begin-sentence tag
        btTable.append([0.0] * len(tagset))

# Initialize the trigram-tag-transition table as 3D matrix
# ttTable[S_{i-2}][S_{i-1}][S_{i}] format
#ttTable = []
#for i in range(len(tagset) + 1): 	
# The last row for the begin-sentence tag
#	ttTable.append([])

#for i in range(len(tagset) + 1):
#	for j in range(len(tagset) + 1): 	
#		# The last row for the begin-sentence tag
#		ttTable[j].append([0.0] * len(tagset))

# Create an empty emission table, as a list of dictionary
# emissionTable[S_{i}][O_{i}] format
#emissionTable = []
#for i in range(len(tagset)):
#        emissionTable.append({})

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

	# Get the tag-id(s) with the count(s) to be added
	# Description: curtagi (Current Tag Index) is a list of
	# tuples, (tagindex, count), where tagindex is the corresponding
	# tagindex in tagset, and count is the count to be added for that
	# tag, which is 1 for normal tags and 0.5 for ambiguous tags
	curtagi = getcounts( bstag )

	# Unigram-tag-transition count
#	utTableCount( curtagi )	
	# Bigram-tag-transition count
	btTableCount( bstagi, curtagi )
	# Trigram-tag-transition count
#	ttTableCount( bstagi, bstagi, curtagi )
	
	# Store the previous word and tag(s)
	prevtagi_2 = bstagi
	prevtagi_1 = curtagi
	prevtag = bstag
	prevword = BSW

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
		
		# Unigram-tag-transition count
#		utTableCount( curtagi )	
		# Bigram-tag-transition count
		btTableCount( prevtagi_1, curtagi )
		# Trigram-tag-transition count
#		ttTableCount( prevtagi_2, prevtagi_1, curtagi )
		# Emission probability count
#		epTableCount( curword, curtagi )

		# If the current word is also a begin-sentence word
		if isEndSentence( prevtag, prevword ):

			# Bigram-tag-transition count
			btTableCount( bstagi, curtagi )
			# Trigram-tag-transition count
#			ttTableCount( bstagi, bstagi, curtagi )
#			ttTableCount( prevtagi_2, bstagi, curtagi )
	
		# Store the current word and tag(s) for next iteration
		prevword = curword
		prevtagi_2 = prevtagi_1
		prevtagi_1 = curtagi
		prevtag = curtag

# Use linear interpolation method for smoothing to find the trigram-probability to avoid sparsity
# -----------------------------------------------------------------------------------------------
# THEORY: 
# $P(s_{k}|s_{k-1},s_{k-2}) = \lambda_{1} P^{ML}(s_{k}) \times \lambda_{2} P^{ML}(s_{k}|s_{k-1})
# \times \lambda_{3} P^{ML}(s_{k}|s_{k-1},s_{k-2})$ where $\lambda_{1}+\lambda_{2}+\lambda_{3}=1$

# Calculating $\lambda_{i}$'s (Refer to the TnT tagger paper, Thorsten Brants)
# n[0] = $\lambda_{1}$ and so on..

#n = [0.0,0.0,0.0]
#N = sum(utTable)
#for i in range(len(tagset)):
#	for j in range(len(tagset)):
#		for k in range(len(tagset)):
#			a = ttTable[i][j][k]	# f(t1,t2,t3)
#			b = btTable[i][j]	# f(t1,t2)
#			c = btTable[j][k]	# f(t2,t3)
#			d = utTable[j]		# f(t2)
#			e = utTable[k]		# f(t3)
#			tmp = max([(float(a-1)/(b-1) if b != 1 else sys.maxint,2),\
#			(float(c-1)/(d-1) if d != 1 else sys.maxint,1),(float(e-1)/(N-1),0)])[1]
#			n[tmp] += a
#n = map(lambda x:x/sum(n),n)

# Normalize the unigram tag-transition table to get the max. likelihood probability
#utTable = map(lambda x:float(x)/sum(utTable) if sum(utTable) != 0 else 0.0, utTable)

# Normalize the bigram tag-transition table to get the max. likelihood probability
btTable = map(lambda row:map(lambda x:float(x)/sum(row) if sum(row) != 0 else 0.0,row),btTable)

# Normalize the trigram tag-transition table to get the max. likelihood probability
#ttTable = map(lambda y:map(lambda row:map(lambda x:float(x)/sum(row) if sum(row) != 0 else 0.0,row),y),ttTable)

# Interpolating with the $\lambda$ values
#for i in range(len(tagset) + 1):
#	for j in range(len(tagset) + 1):
#		for k in range(len(tagset)):
#			ttTable[i][j][k] = n[0] * utTable[k] + n[1] * btTable[j][k] + n[2] * ttTable[i][j][k]

# Normalize the emission table over O_{i} to get the P(O_{i}|S_{i})
#emissionTable = map(lambda row:dict(map(lambda y:(y,float(row[y])/sum(map(lambda x:row[x],row))),row)),emissionTable)

# Form the transpose of this table
#epTable = {}
#for tag in range(len(tagset)):
#        for word, val in emissionTable[tag].items():
#                # If the entry deoesn't exists, create the entry
#                if not(word in epTable):
#                        epTable[word] = [0.0] * len(tagset)
#                epTable[word][tag] = float(val)

# Open trigram-transition table file for writing
try:
	ttmp = open( sys.argv[2], "w" )
#	etmp = open( sys.argv[3], "w" )
except IOError:
	print sys.argv[0],'Couldn\'t open',sys.argv[2],'for writing'
	sys.exit(5)

# Store the interpolated trigram tag-transition probability table
# FORMAT: S_{k-2}_index, S_{k-1}_index : <row of values separated by SPACE>
for j in range(len(tagset) + 1):
	for k in range(len(tagset)):
		ttmp.write( str(btTable[j][k]) + "," )
	ttmp.write( "\n" )

# Store the emission table
# FORMAT: <word>: <row of values separated by SPACE>
#for word, row in epTable.items():
#       etmp.write(word + ":")
#        for val in row:
#                etmp.write(str(val)+" ")
#        etmp.write( "\n" )
