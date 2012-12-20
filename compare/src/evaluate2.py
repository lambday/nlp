#!/usr/bin/env python

import sys
from bnc import tagset, tagdictionary, getcounts, BST, BSW
from util import convertIfNeeded, findMax
from os import listdir, system
from os.path import isfile, join

if (len(sys.argv) < 5):
        print 'Usage:', sys.argv[0], '<wlut> <twlut> [-score<test-corpus-dir>|-demo<model1|model2>'
        sys.exit(1)

# Read the lookup-tables
wLookup = {}
twLookup = []
try:
	lut = open(sys.argv[1],'r')
	for line in lut:
		word = line.strip().split(":")[0]
		wLookup[word] = []
		nextlist = line.strip().split(":")[1].strip().split(" ")
		for nextword in nextlist:
			wLookup[word].append(nextword)
	lut.close()
except IOError:
	print sys.argv[0],'lut-file',sys.argv[1],'doesn\'t exist'
	sys.exit(2)

try:
	lut = open(sys.argv[2],'r')
	i = 0
	for line in lut:
		tmp = line.strip().split(",")[:-1]
		twLookup.append({})
		for wlist in tmp:
			#print wlist.strip().split(":")
			curword = wlist.strip().split(":")[0]
			#print curword
			nextlist = wlist.strip().split(":")[1].strip().split(" ")
			#print nextlist
			twLookup[i][curword] = []
			for nextword in nextlist:
				twLookup[i][curword].append(nextword)
		i += 1
	lut.close()
except IOError:
	print sys.argv[0],'lut-file',sys.argv[2],'doesn\'t exist'
	sys.exit(2)

if sys.argv[3] == "-demo":
	if sys.argv[4] == 'model2':
		system("python tagwords.py tag ems")
		f = open("demotmp","r")
		ip = f.read().strip().split(" ")
		lastword = ip[-1].split("_")[1]
#		print lastword, ip[-1].split("_")
		lasttag = tagdictionary[ip[-1].split("_")[0]]
		if lastword not in twLookup[lasttag]:
			print 'word',lastword,'never appeared with tag',tagset(lasttag)
			sys.exit(0)
		print twLookup[lasttag][lastword]
		f.close()
	elif sys.argv[4] == 'model1':
		print 'Enter the part of the sentence <press ctrl+d to end>'
		line = sys.stdin.readlines()
	        sentence = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
		lastword = sentence[-1]
		if lastword not in wLookup:
			print 'word',lastword,'not in dictionary'
			sys.exit(0)
		print wLookup[lastword]
	else:
        	print sys.argv[0],'Undefined option',sys.argv[3]
	        sys.exit(10)
	
elif sys.argv[3] == "-score":
	# Read the train-corpus directory and put the filenames in corpusFiles
	try:
	        corpusFiles = [ f for f in listdir(sys.argv[4]) if isfile(join(sys.argv[4],f)) ]
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
	                c = open( join(sys.argv[4],corpus), "r" )
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

		 # Get the tag-id(s) with the count(s) to be added
                tagindex = getcounts( bstag )

		# Increment score if correctly guessed
		if bsword in wLookup['^']:
			score1 += 1
		if bsword in twLookup[BST]['^']:
			score2 += 1
		prevword = bsword
		prevtag = bstag
		prevtagi = tagindex

		# Iterate over the corpus for gathering counts
	        for i in range(len(corpus))[1:]:
	                # Get the current tag_word
	                curtag = corpus[i].split("_")[0]
	                curword = convertIfNeeded(corpus[i].split("_")[1],curtag)
		 
			# Get the tag-id(s) with the count(s) to be added
			tagindex = getcounts( curtag )
		
			# Increment score if correctly guessed
			try:
				if curword in wLookup[prevword]:
					score1 += 1
				for tag in prevtagi:
					if curword in twLookup[tag[0]][prevword]:
						score2 += 1
			except KeyError:
				None
			# If the current word is also a begin-sentence word
	                if prevtag == "PUN" and prevword in ['.','?','!']:
				# Increment score if correctly guessed
				if curword in wLookup['^']:
					score1 += 1
				if curword in twLookup[BST]['^']:
					score2 += 1

			prevword = curword
			prevtag = curtag
			prevtagi = tagindex
#	print score1, score2
	try:
		print float(score1) / float(score2)
	except ZeroDivisionError:
		print 0.0

else:
        print sys.argv[0],'Undefined option',sys.argv[3]
        sys.exit(10)
