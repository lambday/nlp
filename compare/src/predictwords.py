#!/usr/bin/env python
#####################
#TODO WRITE A DESCRIPTION OF THIS SCRIPT

import sys
from bnc import tagset, tagdictionary, BSW, BST
from util import convertIfNeeded, findMax, findOneMax
from os import listdir
from os.path import isfile, join, isdir

# Create a lookup table for faster retrieval (bi-gram)
Lookup = {}

# Takes the last seen word and returns most probable word-list/word
def predictUntagged( lastword ):
	if not(lastword in Lookup):
		Lookup[lastword] = findMax(wordTransitionTable[lastword])
	return Lookup[lastword]

# Takes the last seen tag and returns most probable word-list
def predictTagged( lasttag ):
	if not(lasttag in Lookup):
		# The tag has not been listed yet
		try:
			tag = BST if (lasttag == BSW) else tagdictionary[lasttag]
			Lookup[lasttag] = findMax(dict(map(lambda y:(y,sum(map(lambda x:x[0]*x[1],\
			zip(emissionProbTable[y],transitionProbTable[tag])))),emissionProbTable)))
		except KeyError:
			# May be we encountered an ambiguity tag
			if len(lasttag.split("-")) < 2:
				Lookup[lasttag] = ['']
			else:
				lasttag1 = lasttag.split("-")[0]
				lasttag2 = lasttag.split("-")[1]

				tag1 = tagdictionary[lasttag1]	
				tag2 = tagdictionary[lasttag2]	
				if not(lasttag1 in Lookup):
					try:
						Lookup[lasttag1] = findMax(dict(map(lambda y:(y,sum(map(lambda x:x[0]*x[1],\
						zip(emissionProbTable[y],transitionProbTable[tag1])))),emissionProbTable)))
					except KeyError:
						Lookup[lasttag] = ['']
				if not(lasttag2 in Lookup):
					try:
						Lookup[lasttag2] = findMax(dict(map(lambda y:(y,sum(map(lambda x:x[0]*x[1],\
						zip(emissionProbTable[y],transitionProbTable[tag2])))),emissionProbTable)))
					except KeyError:
						Lookup[lasttag] = ['']
				max1 = max(dict(map(lambda y:(y,sum(map(lambda x:x[0]*x[1],\
						zip(emissionProbTable[y],transitionProbTable[tag1])))),emissionProbTable)))
				max2 = max(dict(map(lambda y:(y,sum(map(lambda x:x[0]*x[1],\
					zip(emissionProbTable[y],transitionProbTable[tag2])))),emissionProbTable)))
				Lookup[lasttag] = Lookup[lasttag1] if max1[0] > max2[0] else Lookup[lasttag2]
	return Lookup[lasttag]

# Main script begins
# ------------------

if len( sys.argv ) < 3:
	print 'Usage:',sys.argv[0],'[-tagged|-untagged] [<transition> <emission>|<word-transition>] [optional<test-dir>]'
	sys.exit(1)
# If the first option is untagged, third argument should provide a word-transition-probability file
if sys.argv[1] == "-untagged":
	try:
		wttable = open( sys.argv[2], "r" )
	except IOError:
		print sys.argv[0],'Error: Word Transition file',sys.argv[1],' doesn\'t exist'
		sys.exit(2)
elif sys.argv[1] == "-tagged":
	if len(sys.argv) < 4:
		print sys.argv[0],'With option "-tagged" provide both transition and emission tables'
		sys.exit(1)
	try:
		ttable = open( sys.argv[2], "r" )
		etable = open( sys.argv[3], "r" )
	except IOError:
		print sys.argv[0],'Error: Either',sys.argv[2],'or',sys.argv[3],' doesn\'t exist'
		sys.exit(2)
else:
	print sys.argv[0],'Undefined option specified'
	sys.exit(3)

# Define the tables to avoid NameError
wordTransitionTable = {}
transitionProbTable = []
emissionProbTable = {}

# With the option "-untagged"
if sys.argv[1] == "-untagged":
	# Read the word transition table into a 2-D dictionary
	for line in wttable:
		row = line.strip().split(":")
		nextwords = row[1].strip().split(" ")
		wordTransitionTable[row[0]] = dict(map(lambda x:(x.split(",")[0],float(x.split(",")[1])),nextwords))
	
	# Close the word transition table file
	wttable.close()
# With the option "-tagged"
else:
	# Read the transition table into a 2-D matrix
	for line in ttable:
	        transitionProbTable.append(map(lambda x: float(x),line.strip().split(" ")))
	# Read the emission probability table
	for line in etable:
	        arr = line.strip().split(" ")
	        emissionProbTable[arr[0]] = map( lambda x: float(x), arr[1:] )

	# Close the files
	ttable.close()
	etable.close()

# This part is for Demo
# --------------------
if not(isdir( sys.argv[-1] )):
	if sys.argv[1] == "-untagged":
		print 'Enter the part of the sentence <press ctrl+d to end>'
	else:
		print 'Enter the part of the sentence with POS<press ctrl+d to end>'
	line = sys.stdin.readlines()
	sentence = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
	
	# Demo part
	lastword = BSW
	lasttag = BSW

	# In case the words are untagged
	if sys.argv[1] == "-untagged":
		if len(sentence) != 0:
			lastword = sentence[-1]
		try:
			# Let's assume that we pick the first word from the list
			predictedword = predictUntagged( lastword )
		except KeyError:
			print sys.argv[0],lastword,'doesn\'t exist in our dictionary'
			sys.exit(4)
		sentence.append(predictedword)
	# In case the words are tagged
	else:
		try:
			taggedSentence = map( lambda x: (x.split("_")[0],x.split("_")[1]), sentence )
		except IndexError:
			print sys.argv[0],'You must provide each word as TAG_WORD'
			sys.exit(5)
		if len(taggedSentence) != 0:
			lasttag = taggedSentence[-1][0]
		try:
			# Let's assume that we pick the first max-prob word from the list
			predictedword = predictTagged( lasttag )
			sentence = map( lambda y: y[1], taggedSentence)
			sentence.append(predictedword)
		except KeyError:
			print sys.argv[0],lasttag,'is not a valid tag'
			sys.exit(4)
	guessed = reduce(lambda x,y:x+" "+y,sentence)
	print 'I am guessing you meant:',guessed

# This part is for scoring
# -----------------------
else:
	# Read each of the corpus, then apply the prediction on each of the sentences
	corpusDir = sys.argv[3] if sys.argv[1] == "-untagged" else sys.argv[4]
	try:
		corpusFiles = [ f for f in listdir(corpusDir) if isfile(join(corpusDir,f)) ]
	except OSError:
		print sys.argv[0],'the corpus directory',corpusDir,' doesn\'t exist'
		sys.exit(3)

	# Check if the corpus directory is empty
	if len(corpusFiles) == 0:
        	print sys.argv[0],'Corpus directory',corpusDir,' is empty'
	        sys.exit(4)
	# These two variables are needed for score
	correctGuess = 0
	totalGuess = 0

	# Read one corpus at a time and predict and score
	for corpus in corpusFiles:
		try:
			c = open( join(corpusDir,corpus), "r" )
		except IOError:
			print sys.argv[0],'Error: Couldn\'t read corpus file',corpus
			continue
		# Read the whole corpus as a list of sentences
		try:
			allwords = map( lambda x: (x.split("_")[0],convertIfNeeded(x.split("_")[1],x.split("_")[0])),\
				 c.read().strip().split(" "))
		except IndexError:
			print sys.argv[0],corpus,'not tagged properly'
			continue
		totalGuess += len(allwords)
		sentences = []
		sentence = []
		for i in range(len(allwords)):
			sentence.append(allwords[i])
			if allwords[i][0] == "PUN" and allwords[i][1] in ['.','!','?']:
				sentences.append(sentence)
				sentence = []
		# If the sentence didn't end but the corpus ended anyway
		if sentence != []:
			sentences.append(sentence)
		# Close the corpus file
		c.close()
		
		# For each of the sentences we repeat the following
		for sentence in sentences:
			# Let's start with guessing the first word, preceeded by "^"
			lastword = BSW
			lasttag = BSW
			# Read words in sentences one by one and predict the next word
			for word in sentence:
				# predictedwords are those with highest probabilities
				try:
					predictedword = predictUntagged(lastword) if sys.argv[1] == "-untagged"\
							else predictTagged(lasttag)
					# print word[0],word[1],word[1] in predictedword, 
					# print predictedword if predictedword != [''] else None
					# If the actual word matches with any of the predicted words
					# count it as success
					#if word in predictedwords:
					#	correctGuess += 1
					if word[1] in predictedword:
						correctGuess += 1
					if sys.argv[1] == "-untagged":
						lastword = word[1]
					else:
						lasttag = word[0]
				except KeyError:
					# print sys.argv[0],'new word/tag encountered'
					None

		# print corpus,correctGuess,totalGuess
	try:
		print float(correctGuess)/totalGuess
	except ZeroDivisionError:
		print sys.argv[0],'sentences empty'
