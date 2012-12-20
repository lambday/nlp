#!/usr/bin/env python
##############################################################################
# This script takes the transition probability and emission probability
# files and optionally the corpus directory to be tagged. If the third argument 
# is not specified, it expects the sentence from the stdin. For POS tagging,
# is uses the Viterbi algorithm
##############################################################################

import sys
from bnc import tagset, tagdictionary, getcounts, BST, BSW, isEndSentence
from util import convertIfNeeded
from os import listdir
from os.path import isfile, join

if len( sys.argv ) < 3:
	print 'Usage:',sys.argv[0],'<transition-prob-file> <emission-prob-file> [optional<test-corpus-dir>]\
			 [optional<confusion-matrix-csv(only if test-corpus-dir provided)]'
	sys.exit(1)
try:
	ttmp = open( sys.argv[1], "r" )
	etmp = open( sys.argv[2], "r" )
except IOError:
	print sys.argv[0],'Error: Files',sys.argv[1],'and/or',sys.argv[2],'doesn\'t exist'
	sys.exit(2)

# corpus is a list of words with punctuations
corpus = []
# tagseq is a list of tagseq in the input corpus, used for scoring
tagseq = []

if len( sys.argv ) == 3: 
	# test-corpus not provided, input from stdin
	print 'Enter the sentences <press ctrl+d to end>'
	line = sys.stdin.readlines()
	corpus = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
else:
	if len( sys.argv ) != 5:
		print sys.argv[0],'confusion matrix filename needed'
		sys.exit(1)
	# Read the corpus directory and put the filenames in corpusFiles
	try:
	        corpusFiles = [ f for f in listdir(sys.argv[3]) if isfile(join(sys.argv[3],f)) ]
	except OSError:
	        print sys.argv[0],'the corpus directory doesn\'t exist'
	        sys.exit(2)

	# Check if the corpus directory is empty
	if len(corpusFiles) == 0:
	        print sys.argv[0],'Corpus directory is empty'
	        sys.exit(3)

	for corpusfile in corpusFiles:
        	try:
	                c = open( join(sys.argv[3],corpusfile), "r" )
	        except IOError:
	                print sys.argv[0],'Error: Couldn\'t read corpus file',corpusfile
	                continue
	        # Split for each word_tag combination and append to the corpus list
		temp = c.read().strip().split(" ")
		corpus += map(lambda x:convertIfNeeded(x.split("_")[1],x.split("_")[0]), temp)
	        # Split for each word_tag combination and append to the tagseq list
		tagseq += map(lambda x:x.split("_")[0], temp)
	        # Close the file
	        c.close()

# make the corpusList as to list of sentences
corpusList = []
sentence = []
for i in range(len(corpus)):
	sentence.append(corpus[i])
	if corpus[i] in ['.','!','?',';']:
		corpusList.append(sentence)
		sentence = []
if sentence != []: # if the sentence didn't end but the corpus ended anyway
	corpusList.append(sentence)

# read the transition probability table
transitionProbTable = []
for i in range(len(tagset) + 1):
# The last row for the begin-sentence tag
        transitionProbTable.append([])
for i in range(len(tagset) + 1):
        for j in range(len(tagset) + 1):
                # The last row for the begin-sentence tag
                transitionProbTable[j].append([])
for line in ttmp:
	i = int(line.strip().split(":")[0].split(" ")[0])
	j = int(line.strip().split(":")[0].split(" ")[1])
	transitionProbTable[i][j] = map(lambda x: float(x),line.strip().split(":")[1].split(" "))

# read the emission probability table
emissionProbTable = {}
for line in etmp:
	word = line.strip().split(":")[0]
	arr = line.strip().split(":")[1].split(" ")
	emissionProbTable[word] = map( lambda x: float(x), arr )

# creating an empty output matrix
outputList = []
# creating an empty predicted tagseq matrix
predtagseq = []

########### REPEAT THE FOLLOWING FOR ALL SENTENCES SEPARATELY ################
for sentence in corpusList:
	# create an empty output vector for the current sentence
	output = []
	# create the probability table T1
	T1 = []
	for i in range(len(sentence)):
		T1.append([0] * len(tagset))

	# for the first word, fill up the BSTAGProbability * emissionProbTable[word, tag]	
	word = sentence[0]
#TODO CHECK
#	 print word
#TODO CHECK
	for j in range(len(tagset)):
		try:
			T1[0][j] = transitionProbTable[BST][BST][j] * emissionProbTable[word][j]
		except KeyError:
			# for unknown words, all tags are assumed to have equal probability
			# as their emission probability
			T1[0][j] = transitionProbTable[BST][BST][j] * (1.0/(len(tagset)))

#TODO CHECK
#		if T1[0][j] != 0.0:
#			print tagset[j],T1[0][j]
#TODO CHECK
	
	# create tag table T2
	T2 = []
	for i in range(len(sentence)):
		T2.append([''] * len(tagset))
	
	# the Viterbi algorithm main loop
	#--------------------------------
	# for the next word in the output sequence
	for w in range(1, len(sentence)):
		word = sentence[w]
#TODO CHECK
#		print word
#TODO CHECK
		# for each of the states (tags), to fill up the tables
		for k in range(len(tagset)):
			if word in emissionProbTable:
				ep = emissionProbTable[word][k]
			else:	ep = 1.0/len(tagset)	# Policy for unknown words
			if ep != 0.0:			# To avoid unnecessary computation
#TODO CHECK
#				print tagset[k],ep
#TODO CHECK
				compareMax = []
				# for each of the previous states (tags)
				for j in range(len(tagset)):
					# get the corresponding grandparent state
					try:
						i = tagdictionary[T2[w-1][j]]
					except KeyError:	# '' found, which means use begin-sentence tag
						i = BST
					if T1[w-1][j] != 0.0:
						compareMax.append((transitionProbTable[i][j][k] * T1[w-1][j],j))
#TODO CHECK
#						GP = tagset[i] if i < len(tagset) else "^"
#						print 'tag',tagset[k],'parent',tagset[j],'grandparent',GP,
#						print 'val',str(transitionProbTable[i][j][k]),str(T1[w-1][j]),\
#							str(transitionProbTable[i][j][k] * T1[w-1][j])
#				print 'winner is',tagset[max(compareMax)[1]]
#TODO CHECK
				if len(compareMax) > 0:
					j_max = max(compareMax)
					T1[w][k] = j_max[0] * ep
					T2[w][k] = tagset[j_max[1]]
	
	# trace the T1 and T2 matrices to retrieve the best probable sequence
	# find the max for the last word
	word = sentence[-1]
	z = max(zip(T1[-1], range(len(tagset))))[1]
	output.append(tagset[z] + "_" + word)
	temp = []
	temp.append( tagset[z] )
	for i in range(len(sentence)-1,0,-1):
		word = sentence[i-1]
		try:
			z = tagdictionary[T2[i][z]]
		except KeyError:
			# if the specified tag is '', then mark it as UNC
			z = tagdictionary['UNC']
		output.append(tagset[z] + "_" + word)
		temp.append( tagset[z] )
	output.reverse()
	temp.reverse()
	outputList.append(output)
	predtagseq.append(temp)
######################################################################
# flatten the outputList vector
output = reduce(lambda x,y:x+y,outputList)
# flatten the predicted tag-sequence vector
predtagseq = reduce(lambda x,y:x+y,predtagseq)

# if corpus is provided, save the tagged output as corpusname_tagged.txt
# else print tagged output on stdin
if len(sys.argv) == 3:
	print output
	tmp = open("demotmp","w")
	for tw in output:
		tmp.write(tw+" ")
	tmp.close()
else:
	# Form the confusion matrix
	confusionMatrix = []
	for i in range(len(tagset)):
		confusionMatrix.append([0] * len(tagset))
	for c in zip(tagseq, predtagseq):
		if c[0] in tagdictionary:
			confusionMatrix[tagdictionary[c[0]]][tagdictionary[c[1]]] += 1
		else:	# ambiguity tag encountered
			try:
				a = c[0].split("-")
				if c[1] == a[0]:
					confusionMatrix[tagdictionary[a[0]]][tagdictionary[c[1]]] += 1
				elif c[1] == a[1]:
					confusionMatrix[tagdictionary[a[1]]][tagdictionary[c[1]]] += 1
				else:	# predicted tag totally wrong
					confusionMatrix[tagdictionary[a[0]]][tagdictionary[c[1]]] += 1
					confusionMatrix[tagdictionary[a[1]]][tagdictionary[c[1]]] += 1
			except KeyError:
				print sys.argv[0],'test corpuses are not properly tagged'
				sys.exit(5)
#	print confusionMatrix
	try:
		f = open( sys.argv[4], "w" )
		for row in confusionMatrix:
			for val in row:
				f.write(str(val)+",")
			f.write( "\n" )
		f.close()
	except IOError:
		print sys.argv[0],'couldn\'t write confusion matrix'
