#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary, getcounts, BST, BSW
from util import convertIfNeeded, findMax
from os import listdir
from os.path import isfile, join

if (len(sys.argv) < 4):
        print 'Usage:', sys.argv[0], '<lut-filename> [-score<test-corpus-dir>|-demo<model1|model2>'
        sys.exit(1)

# Read the lookup-table
Lookup = {}
try:
	lut = open(sys.argv[1],'r')
	for line in lut:
		word = line.strip().split(":")[0]
		Lookup[word] = []
		Lookup[word].append(line.strip().split(":")[1].split(",")[0].strip().split(" "))
		Lookup[word].append(line.strip().split(":")[1].split(",")[1].strip().split(" "))
	lut.close()
except IOError:
	print sys.argv[0],'lut-file',sys.argv[1],'doesn\'t exist'
	sys.exit(2)

if sys.argv[2] == "-demo":
	print 'Enter the part of the sentence <press ctrl+d to end>'
	line = sys.stdin.readlines()
        sentence = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
	lastword = sentence[-1]
	if lastword not in Lookup:
		print 'word',lastword,'not in dictionary'
		sys.exit(0)
	if sys.argv[3] == 'model1':
		print Lookup[lastword][0]
	elif sys.argv[3] == 'model2':
		print Lookup[lastword][1]
	else:
        	print sys.argv[0],'Undefined option',sys.argv[3]
	        sys.exit(10)
	
elif sys.argv[2] == "-score":
	# Read the train-corpus directory and put the filenames in corpusFiles
	try:
	        corpusFiles = [ f for f in listdir(sys.argv[3]) if isfile(join(sys.argv[3],f)) ]
	except OSError:
	        print sys.argv[0],'the train corpus directory doesn\'t exist'
	        sys.exit(2)

	# Check if the corpus directory is empty
	if len(corpusFiles) == 0:
	        print sys.argv[0],'Corpus directory is empty'
	        sys.exit(3)

	score1 = 0
	score2 = 0

	# Go through each of the corpus files and gather the counts
	for corpus in corpusFiles:
	        try:
	                c = open( join(sys.argv[3],corpus), "r" )
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

		# Increment score if correctly guessed
		if bsword in Lookup['^'][0]:
			score1 += 1
		if bsword in Lookup['^'][1]:
			score2 += 1
		prevword = bsword
		prevtag = bstag

		# Iterate over the corpus for gathering counts
	        for i in range(len(corpus))[1:]:
	                # Get the current tag_word
	                curtag = corpus[i].split("_")[0]
	                curword = convertIfNeeded(corpus[i].split("_")[1],curtag)
		
			# Increment score if correctly guessed
			try:
				if curword in Lookup[prevword][0]:
					score1 += 1
				if curword in Lookup[prevword][1]:
					score2 += 1
			except KeyError:
				None
			# If the current word is also a begin-sentence word
	                if prevtag == "PUN" and prevword in ['.','?','!']:
				# Increment score if correctly guessed
				if curword in Lookup['^'][0]:
					score1 += 1
				if curword in Lookup['^'][1]:
					score2 += 1

			prevword = curword
			prevtag = curtag
	try:
		print float(score1) / float(score2)
	except ZeroDivisionError:
		print 0.0

else:
        print sys.argv[0],'Undefined option',sys.argv[2]
        sys.exit(10)
