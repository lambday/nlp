#!/usr/bin/env python
#####################
#TODO Description of this script

import sys
from bnc import tagset, tagdictionary, BST
from util import convertIfNeeded
from os import listdir
from os.path import isfile, join

if (len(sys.argv) < 3):
	print 'Usage:', sys.argv[0], '<corpus-dir> <transition-filename> <emission-filename>'
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

# Initialize the tag-transition table as 2D matrix
# transitionTable[S_{i-1}][S_{i}] format
transitionTable = []
for i in range(len(tagset) + 1): 	# one extra row for the begin-sentence tag
        transitionTable.append([0] * len(tagset))

# Create an empty emission table, as a list of dictionary
# emissionTable[S_{i}][O_{i}] format
emissionTable = []
for i in range(len(tagset)):
        emissionTable.append({})

# Go through each of the corpus files and gather the counts
for corpus in corpusFiles:
        try:
                c = open( join(sys.argv[1],corpus), "r" )
        except IOError:
                print sys.argv[0],'Error: Couldn\'t read corpus file',corpus
                continue
        # Split for each word_tag combination and create a list
        corpus = c.read().strip().split(" ")
        # Close the file
        c.close()

	# For the first tag_word, we consider this as begin sentence tag_word
	bstag = corpus[0].split("_")[0]
	bsword = convertIfNeeded(corpus[0].split("_")[1],bstag)
	try:
		i = tagdictionary[bstag]
		transitionTable[BST][i] += 1
		if bsword in emissionTable[i]:
			emissionTable[i][bsword] += 1
		else:	# New word found
			emissionTable[i][bsword] = 1
	except KeyError:	# Most likely ambiguity tag encountered
		if len(bstag.split("-")) > 1:
			bstag_1 = bstag.split("-")[0]
			bstag_2 = bstag.split("-")[1]
			try:
				bstag_i1 = tagdictionary[bstag_1]
				bstag_i2 = tagdictionary[bstag_2]
				transitionTable[BST][bstag_i1] += 0.5
				transitionTable[BST][bstag_i2] += 0.5
				if bsword in emissionTable[bstag_i1]:
					emissionTable[bstag_i1][bsword] += 0.5
				else:	# New word found
					emissionTable[bstag_i1][bsword] = 0.5
				if bsword in emissionTable[bstag_i2]:
					emissionTable[bstag_i2][bsword] += 0.5
				else:	# New word found
					emissionTable[bstag_i2][bsword] = 0.5
			except KeyError:	# undefined tag found
				sys.exit(4)
		else:		# undefined tag found
			sys.exit(4)

	# Iterate over the corpus for gathering counts
	for i in range(len(corpus)-1):
		# For transition table
		tag_1 = corpus[i].split("_")[0]
		tag_2 = corpus[i+1].split("_")[0]
		try:
			i_1 = tagdictionary[tag_1]
			i_2 = tagdictionary[tag_2]
			transitionTable[i_1][i_2] += 1
			# if tag_1 is PUN tag with ?, ! or . as word,
			# then enter the next tag as begin-sentence tag also
			if tag_1 == "PUN" and corpus[i].split("_")[1] in ['.','?','!']:
				transitionTable[BST][i_2] += 1
		except KeyError:	# Most likely ambiguity tag encountered
			if len(tag_1.split("-")) < 2:
				if len(tag_2.split("-")) < 2:	# undefined tag found
					sys.exit(4)
				else:	# tag_2 is the ambiguity tag
					i_1 = tagdictionary[tag_1]
					try:
						i_21 = tagdictionary[tag_2.split("-")[0]]
						i_22 = tagdictionary[tag_2.split("-")[1]]
						transitionTable[i_1][i_21] += 0.5
						transitionTable[i_1][i_22] += 0.5
						# if tag_1 is PUN tag with ?, ! or . as word,
				                # then enter the next tag as begin-sentence tag also
						if tag_1 == "PUN" and corpus[i].split("_")[1] in ['.','?','!']:
							transitionTable[BST][i_21] += 0.5
							transitionTable[BST][i_22] += 0.5
					except KeyError:	# undefined tag found
						sys.exit(4)
			else:	# we assume that PUN cannot be in ambiguous tag
				if len(tag_2.split("-")) < 2:	# only the tag_1 is ambiguous
					i_2 = tagdictionary[tag_2]
					try:
	                                        i_11 = tagdictionary[tag_1.split("-")[0]]
	                                        i_12 = tagdictionary[tag_1.split("-")[1]]
	                                        transitionTable[i_11][i_2] += 0.5
	                                        transitionTable[i_12][i_2] += 0.5
	                                except KeyError:	# undefined tag found
	                                        sys.exit(4)
				else:	# both tag_1 and tag_2 are ambiguous
					try:
	                                        i_11 = tagdictionary[tag_1.split("-")[0]]
	                                        i_12 = tagdictionary[tag_1.split("-")[1]]
						i_21 = tagdictionary[tag_2.split("-")[0]]
	                                        i_22 = tagdictionary[tag_2.split("-")[1]]
	                                        transitionTable[i_11][i_21] += 0.25
	                                        transitionTable[i_11][i_22] += 0.25
						transitionTable[i_12][i_21] += 0.25
	                                        transitionTable[i_12][i_22] += 0.25
	                                except KeyError:	# undefined tag found
	                                        sys.exit(4)	
	
		# For emission table
		word = convertIfNeeded(corpus[i+1].split("_")[1], tag_2)
		try:
			tag_i = tagdictionary[tag_2]
			if word in emissionTable[tag_i]:
				emissionTable[tag_i][word] += 1
			else:	# New word found
				emissionTable[tag_i][word] = 1
		except KeyError:	# Most likely ambiguity tag encountered
			tag_21 = tag_2.split("-")[0]
			tag_22 = tag_2.split("-")[1]
			try:
				tag_i1 = tagdictionary[tag_21]
				tag_i2 = tagdictionary[tag_22]
				if word in emissionTable[tag_i1]:
	                        	emissionTable[tag_i1][word] += 0.5
				else:	# New word found
	                        	emissionTable[tag_i1][word] = 0.5
				if word in emissionTable[tag_i2]:
	                        	emissionTable[tag_i2][word] += 0.5
				else:	# New word found
	                        	emissionTable[tag_i2][word] = 0.5
			except KeyError:	# undefined tag found
				sys.exit(4)

# Normalize the transition table to get the probability
transitionProbTable = map(lambda row:map(lambda x:float(x)/sum(row) if sum(row) != 0 else 0.0,row),transitionTable)

# Normalize the emission table to get the probability
emissionTable = map(lambda row:dict(map(lambda y:(y,float(row[y])/sum(map(lambda x:row[x],row))),row)),emissionTable)

#--------------------------------------
# Form the transpose of this table
emissionProbTable = {}
for tag in range(len(tagset)):
	for word,val in emissionTable[tag].items():
		# If the entry deoesn't exists, create the entry
		if not(word in emissionProbTable):
			emissionProbTable[word] = [0.0] * len(tagset)
		emissionProbTable[word][tag] = float(val)
#--------------------------------------

# Open transition and emission table files for writing
try:
	ttmp = open( sys.argv[2], "w" )
	etmp = open( sys.argv[3], "w" )
except IOError:
	print sys.argv[0],'Couldn\'t open',sys.argv[2],'and',sys.argv[3],'for writing'
	sys.exit(5)

# Store the transition probability table
for row in transitionProbTable:
	for val in row:
		ttmp.write(str(val)+" ")
	ttmp.write("\n")

#--------------------------------------
# Store the emission probability table
# for row in emissionTable:
#	for word,val in row.items():
#		etmp.write(word + ":" + str(val) + " ")
#	etmp.write("\n")
#--------------------------------------

# Store the transpose of emission probability table
for word, row in emissionProbTable.items():
        etmp.write(word + " ")
        for val in row:
                etmp.write(str(val)+" ")
        etmp.write("\n")

# Close the files after writing
ttmp.close()
etmp.close()
