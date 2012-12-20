#!/usr/bin/env python
#####################
# This script reads a single corpus and calculates the transition and emission
# tables. For first run, it assumes a transition file filled with zeros, and it
# adds the new occurances with the existing ones. For emissiont table, if the 
# word exists in the table, it adds the new occurances, otherwise adds a row for
# the newly encountered word

import sys
from bnc import tagset, tagdictionary

if (len(sys.argv) < 3):
	print 'Usage:', sys.argv[0], '<corpus-name> <transition-filename> <emission-filename>'
	sys.exit(1)
try:
	c = open( sys.argv[1], "r" )
	ttmp = open( sys.argv[2], "r" )
except IOError:
	print sys.argv[0],'Error: Input file doesn\'t exist'
	sys.exit(2)

emissionTable={}
# if emission file exists, read it as a dictionary
try:
	etmp = open( sys.argv[3], "r" )
	for line in etmp:
		arr = line.strip().split(" ")
		emissionTable[arr[0]] = map( lambda x: float(x), arr[1:] )
except IOError:
	None

corpus = c.read().strip().split(" ")

# read the transition table as float 2d matrix
transitionTable = []
for line in ttmp:
	transitionTable.append(map(lambda x: float(x),line.strip().split(" ")))

# close the tmp files and open for writing
try:
	ttmp.close()
	ttmp = open( sys.argv[2], "w" )
	try:
		etmp.close()
	except NameError:
		None
	etmp = open( sys.argv[3], "w" )
except IOError:
	sys.exit(3)

BST = len(tagset)
# for the first tag, enter in the first row (begin-sentence tag)
bstag = corpus[0].split("_")[0]
try:
	i = tagdictionary[bstag]
	transitionTable[BST][i] += 1
except KeyError:
	# ambiguity tag encountered
	if len(bstag.split("-")) > 1:
		tag_1 = bstag.split("-")[0]
		tag_2 = bstag.split("-")[1]
		try:
			tag_i1 = tagdictionary[tag_1]
			tag_i2 = tagdictionary[tag_2]
			transitionTable[BST][tag_i1] += 0.5
			transitionTable[BST][tag_i2] += 0.5
		except KeyError:
			# undefined tag found
			sys.exit(4)
	else:		# undefined tag found
		sys.exit(4)

	
# iterate over the corpus for transition table
for i in range(len(corpus)-1):
	tag_1 = corpus[i].split("_")[0]
	tag_2 = corpus[i+1].split("_")[0]
	try:
		i_1 = tagdictionary[tag_1]
		i_2 = tagdictionary[tag_2]
		transitionTable[i_1][i_2] += 1
		# if tag_1 is PUN tag with ?, ! or . as word,
		# then enter these as begin-sentence tag also
		if tag_1 == "PUN":
			word = corpus[i].split("_")[1]
			if word == '.' or word == '?' or word == '!':
				transitionTable[BST][i_2] += 1
	except KeyError:
		# ambiguity tag encountered
		if len(tag_1.split("-")) < 2:
			if len(tag_2.split("-")) < 2:
				# undefined tag found
				sys.exit(4)
			else:	# tag_2 is the ambiguity tag
				i_1 = tagdictionary[tag_1]
				try:
					i_21 = tagdictionary[tag_2.split("-")[0]]
					i_22 = tagdictionary[tag_2.split("-")[1]]
					transitionTable[i_1][i_21] += 0.5
					transitionTable[i_1][i_22] += 0.5
					# if tag_1 is PUN tag with ?, ! or . as word,
			                # then enter these as begin-sentence tag also
			                if tag_1 == "PUN":
                        			word = corpus[i].split("_")[1]
			                        if word == '.' or word == '?' or word == '!':
			                                transitionTable[BST][i_21] += 0.5
			                                transitionTable[BST][i_22] += 0.5
				except KeyError:
					# undefined tag found
					sys.exit(4)
		else:
			if len(tag_2.split("-")) < 2:
				# only the tag_1 is ambiguous
				i_2 = tagdictionary[tag_2]
				try:
                                        i_11 = tagdictionary[tag_1.split("-")[0]]
                                        i_12 = tagdictionary[tag_1.split("-")[1]]
                                        transitionTable[i_11][i_2] += 0.5
                                        transitionTable[i_12][i_2] += 0.5
                                except KeyError:
                                        # undefined tag found
                                        sys.exit(4)
			else:
				# both tag_1 and tag_2 are ambiguous
				try:
                                        i_11 = tagdictionary[tag_1.split("-")[0]]
                                        i_12 = tagdictionary[tag_1.split("-")[1]]
					i_21 = tagdictionary[tag_2.split("-")[0]]
                                        i_22 = tagdictionary[tag_2.split("-")[1]]
                                        transitionTable[i_11][i_21] += 0.25
                                        transitionTable[i_11][i_22] += 0.25
					transitionTable[i_12][i_21] += 0.25
                                        transitionTable[i_12][i_22] += 0.25
                                except KeyError:
                                        # undefined tag found
                                        sys.exit(4)	

# iterate over the corpus for emission table
for i in range(len(corpus)):
	tag = corpus[i].split("_")[0]
	word = corpus[i].split("_")[1].lower()
	try:
		tag_i = tagdictionary[tag]
		try:
			emissionTable[word][tag_i] += 1
		except KeyError:
			# new word found
			emissionTable[word] = [0] * len(tagset)
			emissionTable[word][tag_i] += 1
	except KeyError:
		# ambiguity tag encountered
		tag_1 = tag.split("-")[0]
		tag_2 = tag.split("-")[1]
		try:
			tag_i1 = tagdictionary[tag_1]
			tag_i2 = tagdictionary[tag_2]
			try:
                        	emissionTable[word][tag_i1] += 0.5
                        	emissionTable[word][tag_i2] += 0.5
			except KeyError:
				# new word found
				emissionTable[word] = [0] * len(tagset)
				emissionTable[word][tag_i1] = 0.5
				emissionTable[word][tag_i2] = 0.5
		except KeyError:
			# undefined tag found
			sys.exit(4)

# store the transition table
for row in transitionTable:
	for val in row:
		ttmp.write(str(val)+" ")
	ttmp.write("\n")

# store the emission table
for word, row in emissionTable.items():
	etmp.write(word + " ")
	for val in row:
		etmp.write(str(val)+" ")
	etmp.write("\n")
