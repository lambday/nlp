#!/usr/bin/env python
#####################
# this script takes the transition probability and emission probability
# files and optionally the corpus to be tagged. if the third argument is
# not specified, it expects the sentence from the stdin. For POS tagging,
# is uses the Viterbi algorithm and A* and compares the result

import sys
from bnc import tagset, tagdictionary, PunWordList, isEndSentence, BSW, BST, getcounts
from util import convertIfNeeded, findMax
from math import log
from subprocess import check_output, CalledProcessError, STDOUT
import subprocess
from termios import tcflush, TCIOFLUSH
from os import listdir
from os.path import isfile, join

def calcProbability( ls ):
	w = map(lambda x:x.split("_")[1], ls)
	t = map(lambda x:tagset.index(x.split("_")[0]), ls)
	ret = -log(transitionProbTable[BST][t[0]])
	ret += -log(emissionProbTable[w[0]][t[0]] if w[0] in emissionProbTable else 1.0/len(tagset))
	for i in range(len(w))[:-1]:
		ret += -log(transitionProbTable[t[i]][t[i+1]])
		ret += -log(emissionProbTable[w[i+1]][t[i+1]] if w[i+1] in emissionProbTable else 1.0/len(tagset))
	return ret

if len( sys.argv ) < 3:
	print 'Usage:',sys.argv[0],'<transition-prob-file> <emission-prob-file> [optional<test-corpus>]'
	sys.exit(1)
try:
	ttmp = open( sys.argv[1], "r" )
	etmp = open( sys.argv[2], "r" )
except IOError:
	print sys.argv[0],'Error: Files doesn\'t exist'
	sys.exit(2)
# make the corpusList as to list of sentences
sentenceList = []
tagList = []
sentence = []
tags = []
if len( sys.argv ) == 3: # test-corpus not provided, input from stdin
	print 'Enter the sentences <press ctrl+d to end>'
	line = sys.stdin.readlines()
	corpus = reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))
	for i in range(len(corpus)):
		sentence.append(corpus[i])
		if corpus[i] in PunWordList:
			sentenceList.append(sentence)
			sentence = []
	if sentence != []: # if the sentence didn't end but the corpus ended anyway
		None	#currently not considering the sentences that ended not with PUN
else:
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

	corpus = []
	for cor in corpusFiles:
	        try:
        	        c = open( join(sys.argv[3],cor), "r" )
	        except IOError:
        	        print sys.argv[0],'Error: Couldn\'t read corpus file',cor
	                continue
	        # Split for each word_tag combination and create a list
	        corpus += c.read().strip().split(" ")
	        # Close the file
	        c.close()

	for i in range(len(corpus)):
		sentence.append(convertIfNeeded( corpus[i].split("_")[1],corpus[i].split("_")[0] ))
		tags.append(corpus[i].split("_")[0])
		if corpus[i].split("_")[1] in PunWordList:
			sentenceList.append(sentence)
			tagList.append(tags)
			sentence = []
			tags = []
	if sentence != []: # if the sentence didn't end but the corpus ended anyway
		#corpusList.append(sentence)
		None	#currently not considering the sentences that ended not with PUN
#print sentenceList

# read the transition probability table
transitionProbTable = []
for line in ttmp:
	transitionProbTable.append(map(lambda x: float(x),line.strip().split(",")[:-1]))

#TEST
#print transitionProbTable
#for t in range(len(tagset)+1):
#	for k in range(len(tagset)):
#		print transitionProbTable[t][k],
#	print "\n"
#sys.exit(0)

# read the emission probability table
emissionProbTable = {}
for line in etmp:
	arr = line.strip().split(":")
	emissionProbTable[arr[0]] = map( lambda x: float(x), arr[1].strip().split(" ") )

# TEST
#for w, l in emissionProbTable.items():
#	print w,len(l)
#	break
#sys.exit(0)

# BST points to the begin-sentence probabilties in transition table
BST = len(tagset)

# creating an empty output matrix
outputList = []
resultList = []

# calculate $e^{PUN}_{min}$
# to pass this as per the correct punctuation for a sentence :P
ePunList = {}
p = tagset.index('PUN')
for punWord in PunWordList:
	try:
		ePunList[punWord] = -log(max(map(lambda t:transitionProbTable[t][p],\
			range(len(tagset))))*emissionProbTable[punWord][p])
	except ValueError:
		ePunList[punWord] = sys.maxint
#print ePunList
#sys.exit(0)

########### REPEAT THE FOLLOWING FOR ALL SENTENCES SEPARATELY ################
for sentence in sentenceList:
	#### RUN THE VITERBI ALGORITHM ####

	# create an empty output vector for the current sentence
	output = []
	# create the probability table T1
	T1 = []
	for i in range(len(sentence)):
		T1.append([0] * len(tagset))
		# for the first word, fill up the BSTAGProbability * emissionProbTable[word, tag]
		if i == 0:
			word = sentence[i]
			for j in range(len(tagset)):
				try:
					T1[i][j] = transitionProbTable[BST][j] * emissionProbTable[word][j]
				except KeyError:
					# for unknown words, all tags are assumed to have equal probability
					# as their emission probability
					T1[i][j] = transitionProbTable[BST][j] * (1.0/(len(tagset)))
	
	# create tag table T2
	T2 = []
	for i in range(len(sentence)):
		T2.append([''] * len(tagset))
	
	# the Viterbi algorithm main loop
	#--------------------------------
	# for the next word in the output sequence
	for i in range(1, len(sentence)):
		word = sentence[i]
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
	word = sentence[-1]
	z = max(zip(T1[-1], range(len(tagset))))[1]
	output.append(tagset[z] + "_" + word)
	for i in range(len(sentence)-1,0,-1):
		word = sentence[i-1]
		try:
			z = tagdictionary[T2[i][z]]
		except KeyError:
			# if the specified tag is '', then mark it as UNC
			z = tagdictionary['UNC']
		output.append(tagset[z] + "_" + word)
	output.reverse()
	outputList.append(output)
#	print output
	
	#### RUN THE A* ALGORITHM ####

	# find the $e_{min}$ and $e^{i}_{min}$
	i = 0
	minList = []
	tempETable = []
	for word in sentence[:-1]:
		temp = map(lambda cur_t:max(map(lambda nxt_t:transitionProbTable[cur_t][nxt_t]\
		*emissionProbTable[word][nxt_t] if word in emissionProbTable else \
		transitionProbTable[cur_t][nxt_t]/float(len(tagset)),range(len(tagset)))),range(len(tagset)+1))
		if i == 0:
			minList.append( -log(temp[-1]) )
		else:
			minList.append( -log(max(temp[:-1])) )
		i += 1
		try:
			tempETable.append((word,emissionProbTable[word]))
		except KeyError:
			tempETable.append((word,[1.0/len(tagset)] * len(tagset)))
	minList.append( ePunList[sentence[-1]] )
	tempETable.append((sentence[-1],emissionProbTable[sentence[-1]]))

	# Store the emission table
	# FORMAT: <word>: <row of values separated by SPACE>
	f = open( "emps", "w" )
	for row in tempETable:
	       	f.write(row[0] + ":")
	        for val in row[1]:
	                f.write(str(val)+" ")
	        f.write( "\n" )
	f.close() #CULPRIT
	
	# form the command line arg string
	cmd = ['java', 'AStar']
	for val in minList:
		cmd.append( str(val) )
	#print cmd
	try:
		result = map(lambda x:int(x),check_output(cmd).strip().split("\n"))[:-1]
		result.reverse()
		result = map(lambda x:tagset[result[x]]+"_"+sentence[x],range(len(sentence)))
		resultList.append(result)
	except CalledProcessError:
		print 'Could not launch AStar.class'

	tcflush( sys.stdin, TCIOFLUSH )
#	print result

######################################################################

# if corpus is provided, save the tagged output as corpusname_tagged.txt
# else print tagged output on stdin
if len(sys.argv) == 3:
	# flatten the outputList vector
	output = reduce(lambda x,y:x+y,outputList)
	result = reduce(lambda x,y:x+y,resultList)

	print output
	print result

	if output != result:
		print 'Different results'
		# Calculate the probabilities of the two paths
		print calcProbability( output )
		print calcProbability( result )
else:
	score1 = 0.0
	score2 = 0.0
	for i in range(len(tagList)):
		score1 += sum(map(lambda x:1 if outputList[i][x].split("_")[0]==tagList[i][x] else 0,range(len(tagList[i]))))
		score2 += sum(map(lambda x:1 if resultList[i][x].split("_")[0]==tagList[i][x] else 0,range(len(tagList[i]))))
	print score1 / score2
		
	for i in range(len(outputList)):
		if outputList[i] != resultList[i]:
			print 'Different results'
			# Calculate the probabilities of the two paths
			print outputList[i]
			print calcProbability( outputList[i] )
			print resultList[i]
			print calcProbability( resultList[i] )
			print tagList[i]
#	name = reduce(lambda x,y:x+'.'+y,sys.argv[3].split(".")[:-1]) + "_tagged." + sys.argv[3].split(".")[-1]
#	opfile = open( name, "w" )
#	for word in output:
#		opfile.write(word+" ")
