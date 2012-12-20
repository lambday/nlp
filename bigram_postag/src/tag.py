#!/usr/bin/env python
#####################
# this script takes the transition probability and emission probability
# files and optionally the corpus to be tagged. if the third argument is
# not specified, it expects the sentence from the stdin. For POS tagging,
# is uses the Viterbi algorithm

import sys
from bnc import tagset, tagdictionary

if len( sys.argv ) < 3:
	print 'Usage:',sys.argv[0],'<transition-prob-file> <emission-prob-file> [optional<test-corpus>]'
	sys.exit(1)
try:
	ttmp = open( sys.argv[1], "r" )
	etmp = open( sys.argv[2], "r" )
except IOError:
	print sys.argv[0],'Error: Files doesn\'t exist'
	sys.exit(2)
if len( sys.argv ) == 3: # test-corpus not provided, input from stdin
	print 'Enter the sentences <press ctrl+d to end>'
	line = sys.stdin.readlines()
	temp = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
	corpus = map( lambda x: x.lower(), temp )
else:
	try:
		c = open( sys.argv[3], "r" )
		corpus = map( lambda x: x.split("_")[1].lower(), c.read().strip().split(" "))
	except IOError:
        	print sys.argv[0],'Error: test corpus file doesn\'t exist'
	        sys.exit(3)

# make the corpusList as to list of sentences
corpusList = []
sentence = []
for i in range(len(corpus)):
	sentence.append(corpus[i])
	if corpus[i] == '.' or corpus[i] == '!' or corpus[i] == '?':
		corpusList.append(sentence)
		sentence = []
if sentence != []: # if the sentence didn't end but the corpus ended anyway
	corpusList.append(sentence)
# print corpusList

# read the transition probability table
transitionProbTable = []
for line in ttmp:
	transitionProbTable.append(map(lambda x: float(x),line.strip().split(" ")))

# read the emission probability table
emissionProbTable = {}
for line in etmp:
	arr = line.strip().split(" ")
	emissionProbTable[arr[0]] = map( lambda x: float(x), arr[1:] )

# BST points to the begin-sentence probabilties in transition table
BST = len(tagset)

# creating an empty output matrix
outputList = []

########### REPEAT THE FOLLOWING FOR ALL SENTENCES SEPARATELY ################
for corpus in corpusList:
	# create an empty output vector for the current sentence
	output = []
	# create the probability table T1
	T1 = []
	for i in range(len(corpus)):
		T1.append([0] * len(tagset))
		# for the first word, fill up the BSTAGProbability * emissionProbTable[word, tag]
		if i == 0:
			word = corpus[i]
			for j in range(len(tagset)):
				try:
					T1[i][j] = transitionProbTable[BST][j] * emissionProbTable[word][j]
				except KeyError:
					# for unknown words, all tags are assumed to have equal probability
					# as their emission probability
					T1[i][j] = transitionProbTable[BST][j] * (1.0/(len(tagset)))
	
	# create tag table T2
	T2 = []
	for i in range(len(corpus)):
		T2.append([''] * len(tagset))
	
	# the Viterbi algorithm main loop
	#--------------------------------
	# for the next word in the output sequence
	for i in range(1, len(corpus)):
		word = corpus[i]
		# for each of the states (tags)
		for j in range(len(tagset)):
			# find the max of transitionProbability[k,currentTag] *
			# emissionProbability[currentTag,currentWord] * T1[k,i-1]
			try:
				if emissionProbTable[word][j] != 0.0:
					k_max = max([(transitionProbTable[k][j]*T1[i-1][k],k) for k in range(len(tagset))])
					T1[i][j] = k_max[0] * emissionProbTable[word][j]
					T2[i][j] = tagset[k_max[1]]
			except KeyError: # the word doesn't occur in the training set
					 # assume uniform probability for all tags for that word
					k_max = max([(transitionProbTable[k][j]*T1[i-1][k],k) for k in range(len(tagset))])
	                                T1[i][j] = k_max[0] * (1.0/(len(tagset)))
	                                T2[i][j] = tagset[k_max[1]]
	# trace the T1 and T2 matrices to retrieve the best probable sequence
	# find the max for the last word
	word = corpus[-1]
	z = max(zip(T1[-1], range(len(tagset))))[1]
	output.append(tagset[z] + "_" + word)
	for i in range(len(corpus)-1,0,-1):
		word = corpus[i-1]
		try:
			z = tagdictionary[T2[i][z]]
		except KeyError:
			# if the specified tag is '', then mark it as UNC
			z = tagdictionary['UNC']
		output.append(tagset[z] + "_" + word)
	output.reverse()
	outputList.append(output)
######################################################################
# flatten the outputList vector
output = reduce(lambda x,y:x+y,outputList)

# if corpus is provided, save the tagged output as corpusname_tagged.txt
# else print tagged output on stdin
if len(sys.argv) == 3:
	print output
else:
	name = reduce(lambda x,y:x+'.'+y,sys.argv[3].split(".")[:-1]) + "_tagged." + sys.argv[3].split(".")[-1]
	opfile = open( name, "w" )
	for word in output:
		opfile.write(word+" ")
