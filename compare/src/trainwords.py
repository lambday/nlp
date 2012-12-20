#!/usr/bin/env python
#####################
#TODO Write a description of this script
#

import sys
from bnc import tagset, tagdictionary, BSW
from util import convertIfNeeded
from os import listdir
from os.path import isfile, join

# Main script begins
# ------------------
if (len(sys.argv) < 3):
	print 'Usage:', sys.argv[0], '<corpus-dir> <word-transition-filename>'
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

# Create an empty word-transition table, as a 2-D dictionary
wordTransitionTable = {}

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
	# For first word in the corpus, we consider this as a BSW
	bsword = convertIfNeeded(corpus[0].split("_")[1],corpus[0].split("_")[0]) #The format is TAG_WORD
	
	try:
		wordTransitionTable[BSW][bsword] += 1
	except KeyError:
		# The entry word_1,word_2 is not there in the table
		try:
			wordTransitionTable[BSW][bsword] = 1
		except KeyError:
			# No entry for word_1 is found, create a new entry
			wordTransitionTable[BSW] = {}
			wordTransitionTable[BSW][bsword] = 1
	# iterate over the corpus for word transition table
	for i in range(len(corpus)-1):
		word_1 = convertIfNeeded(corpus[i].split("_")[1],corpus[i].split("_")[0])
		word_2 = convertIfNeeded(corpus[i+1].split("_")[1],corpus[i+1].split("_")[0])
		# Find the tag of the first word, we need it to find the counts 
		# for words that start sentences in case the tag is PUN
		tag_1 = corpus[i].split("_")[0]
		try:
			wordTransitionTable[word_1][word_2] += 1
		except KeyError:
			# The entry word_1,word_2 is not there in the table
			try:
				wordTransitionTable[word_1][word_2] = 1
			except KeyError:
				# No entry for word_1 is found, create a new entry
				wordTransitionTable[word_1] = {}
				wordTransitionTable[word_1][word_2] = 1
		# if tag_1 is PUN tag with ?, ! or . as word_1,
		# then enter this as begin-sentence word
		if tag_1 == "PUN":
			if word_1 == '.' or word_1 == '?' or word_1 == '!':
				try:
					wordTransitionTable[BSW][word_2] += 1
				except KeyError:
					# The entry BST,bsword is not there in the table
					wordTransitionTable[BSW][word_2] = 1

# Calculate the word transition probability
# normalize the emission table to get the probability

# Get counts per tag in totalCounts
totalCounts=dict(map(lambda x:(x,sum(map(lambda y:wordTransitionTable[x][y],wordTransitionTable[x]))),wordTransitionTable))

for currentword, nextWordList in wordTransitionTable.items():
	for nextword, count in nextWordList.items():
		try:
			wordTransitionTable[currentword][nextword] /= float(totalCounts[currentword])
		except ZeroDivisionError:
			wordTransitionTable[currentword][nextword] = 0.0
		except KeyError:
			print sys.argv[0],'Something unexpected happened :('
			sys.exit(4)	

# Store the word-transition table
try:
	wttable = open( sys.argv[2], "w" )
except IOError:
	print sys.argv[0],'Could not open transition table file for writing'
	sys.exit(5)

for word, row in wordTransitionTable.items():
	wttable.write(word + ":")
	for nextword, prob in row.items():
		wttable.write(nextword+","+str(prob)+" ")
	wttable.write("\n")

# Close the open files
wttable.close()
