#!/usr/bin/env python
#############################################################################
# This script calculates the probability values $P(O_{k}|S_{k},O_{k-1})$
# $P(O_{k}|O_{k-1})$ and $P(S_{k}|S_{k-1})$. It gathers the counts in 
# tagged-word-transition-table (twtTable), word-transition-table (wtTable) 
# and tag-transition-table (ttTable). Finally, it creates two look-up tables, 
# wlut (word-lut) and twlut (tagged-word-lut) and saves these two.
#############################################################################

import sys
import math
from bnc import tagset, tagdictionary, getcounts, BST, BSW
from util import convertIfNeeded, findMax
from os import listdir
from os.path import isfile, join

def wtTableCount( prevword, curword ):
	# Word-transition count
	if prevword in wtTable:
		if curword in wtTable[prevword]:
			wtTable[prevword][curword] += 1
		else:	wtTable[prevword][curword] = 1
	else:
		wtTable[prevword] = {}
		wtTable[prevword][curword] = 1

def ttAndtwtTableCount( prevtagi, prevword, curtagi, curword ):
	for i in curtagi:
		# Tag-transition count
		for j in prevtagi:
			ttTable[j[0]][i[0]] += j[1] * i[1]
		# Tagged-word-transition count
		if prevword in twtTable[i[0]]:
			if curword in twtTable[i[0]][prevword]:
				twtTable[i[0]][prevword][curword] += i[1]
			else:	twtTable[i[0]][prevword][curword] = i[1]
		else:	
			twtTable[i[0]][prevword] = {}
			twtTable[i[0]][prevword][curword] = i[1]

minval = 0.0 #1e-100 #sys.float_info.min

def marginalizeOverTags( sentence ):
	if len( sentence ) < 2:
		return 1
	
	# Initialize the marginal with emission probabilities
	marginal = []
	for t in range(len(tagset)):
		try:
			marginal.append( twtTable[t][sentence[-2]][sentence[-1]] )
		except KeyError:
			marginal.append( minval )

	# Iterate over the sentence from backwords to calculate the marginal
	for k in range(len(sentence),0,-1)[2:]:
		temp = []
		tempEmission = []
		for t in range(len(tagset)):
			temp.append(sum(p*q for p,q in zip(ttTable[t], marginal)))
			try:
				tempEmission.append( twtTable[t][sentence[k-1]][sentence[k]] )
			except KeyError:
				tempEmission.append( minval )
		
		marginal = map(lambda x:x[0]*x[1],zip(temp, tempEmission))
	marginal = sum(p*q for p,q in zip(ttTable[BST], marginal))

	return marginal

# Main script begins
#############################################################################
# Takes 3 or 4 arguments depending on whether we're running this script for scoring
# or demo. If option "-score" is given, then test-corpus directory has to be provided. 
# With 'score' option we find the probability of the word sequence in the test-corpus 
# and calculate the perplexity for both word-based and tagged-word based predictor.
# With "-demo", we crete a word-lookup table and tagged-word lookup table and store.
#############################################################################
# With 'demo', we take transition and emission probability filenames
# as inputs and run our tagger to tag the words that the user provides. Then we predict
# the next word with maximum probability, based on words or tagged-words, as per users'
# choice from a menu. 


if (len(sys.argv) < 4):
	print 'Usage:', sys.argv[0], '<train-corpus-dir> <test-corpus-dir> <lut-filename>'
	sys.exit(1)

# Read the train-corpus directory and put the filenames in corpusFiles
try:
        corpusFiles = [ f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1],f)) ]
except OSError:
        print sys.argv[0],'the train corpus directory doesn\'t exist'
        sys.exit(2)

# Check if the corpus directory is empty
if len(corpusFiles) == 0:
        print sys.argv[0],'Corpus directory is empty'
        sys.exit(3)

# Initialize the tag-transition table as 2D matrix
# ttTable[S_{i-1}][S_{i}] format
ttTable = []
for i in range(len(tagset) + 1): 	
# The last row for the begin-sentence tag
        ttTable.append([0] * len(tagset))

# Create the word-transition table as 2D hashmap
# wtTable[O_{i-1}][O_{i}] format
wtTable = {}

# Create tagged-word-transition table, as a list of hashmap of hashmap
# twtTable[S_{i}][O_{i-1}][O_{i}] format
twtTable = []
for i in range(len(tagset)):
        twtTable.append({})

# Create a wordlist
wordlist = {}
wordlist['^'] = None

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
	# Word-transition count
	wtTableCount( BSW, bsword )

	# add to the wordlist
	if bsword not in wordlist:
		wordlist[bsword] = None

	# Get the tag-id(s) with the count(s) to be added
	tagindex = getcounts( bstag )
	# Tag-transition and tagged-word-transition count
	ttAndtwtTableCount( [(BST,1.0)], BSW, tagindex, bsword )

	# Store the previous word and tag(s)
	prevword = bsword
	prevtagi = tagindex
	prevtag = bstag

	# Iterate over the corpus for gathering counts
	for i in range(len(corpus))[1:]:
		# Get the current tag_word
		curtag = corpus[i].split("_")[0]
		curword = convertIfNeeded(corpus[i].split("_")[1],curtag)
		# Word-transition count
		wtTableCount( prevword, curword )

		# add to the wordlist
		if curword not in wordlist:
			wordlist[curword] = None

		# Get the tag-id(s) with the count(s) to be added
		tagindex = getcounts( curtag )
		# Tag-transition and tagged-word-transition count
		ttAndtwtTableCount( prevtagi, prevword, tagindex, curword )

		# If the current word is also a begin-sentence word
		if prevtag == "PUN" and prevword in ['.','?','!']:
			# Word-transition count
			wtTableCount( BSW, curword )

			# Tag-transition and tagged-word-transition count
			ttAndtwtTableCount( [(BST,1.0)], BSW, tagindex, curword )
	
		# Store the current word and tag(s) for next iteration
		prevword = curword
		prevtagi = tagindex
		prevtag = curtag

# Normalize the tag-transition table to get the probability
ttTable = map(lambda row:map(lambda x:float(x)/sum(row) if sum(row) != 0 else 0.0,row),ttTable)

# Normalize the word-transition table to get the probability
totalCounts=dict(map(lambda x:(x,sum(map(lambda y:wtTable[x][y],wtTable[x]))),wtTable))
for prevword, curWordList in wtTable.items():
        for curword, count in curWordList.items():
                try:
			#TODO
			# Add-one smoothing technqiue
                        wtTable[prevword][curword] = (count) / (float(totalCounts[prevword]))
                except ZeroDivisionError:
                        wtTable[prevword][curword] = 0.0

# Normalize the tagged-word-transition table to get the probability
totalCounts=map(lambda t:dict(map(lambda x:(x,sum(map(lambda y:twtTable[t][x][y],\
		twtTable[t][x]))),twtTable[t])),range(len(tagset)))
for i in range(len(tagset)):
	for prevword, curWordList in twtTable[i].items():
		for curword, count in curWordList.items():
			try:
				#TODO
				# Add-one smoothing technqiue
				twtTable[i][prevword][curword] = (count) / (float(totalCounts[i][prevword]))
			except ZeroDivisionError:
                        	twtTable[i][prevword][curword] = 0.0
#############################################################################
# validation for ttTable
#############################################################################
#for t in range(len(tagset)):
#	total = 0
#	for k in ttTable[t]:
#		total += k
#	print total
#############################################################################
# validation for wtTable
#############################################################################
#for prevword, curWordList in wtTable.items():
#	total = 0
#	for curword, prob in curWordList.items():
#		total += prob
#	print total
#############################################################################
# validation for twtTable
#############################################################################
#for i in range(len(tagset)):
#	for prevword, curWordList in twtTable[i].items():
#		total = 0
#		for curword, prob in curWordList.items():
#			total += prob
#		print total
#############################################################################
#print totalCounts
#for i in range(len(tagset)):
#	print tagset[i],"=",
#	for prevword, curWordList in twtTable[i].items():
#		print prevword,"::",curWordList,
#		for curword, prob in curWordList.items():
#			print prob
#	print "\n"

#print ttTable
#for key, val in wtTable.items():
#	print key,":",val
#print wtTable
#for tag in range(len(tagset)):
#	print tagset[tag],twtTable[tag]# if 'are' in twtTable[tag] else None
#sys.exit(0)
#############################################################################

# For demo purpose
#############################################################################
# Create a look-up table, Lookup[currentword] will contain two lists.
# The first containing the most probable word using model 1 and the
# second list for model 2
Lookup = {}

# Iterate over all words
for word, val in wordlist.items():
	Lookup[word] = []
	# Find the argmax using model 1
	try:
		Lookup[word].append(findMax(wtTable[word]))
	except KeyError:
		Lookup[word].append([])
	# Find the argmax using model 2
	tempEmission = []
	temp = {}
	temp[word] = {}
	try:
		for nextword, p in wtTable[word].items():
			for t in range(len(tagset)):
				try:
					tempEmission.append(twtTable[t][word][nextword])
				except KeyError:
					tempEmission.append(minval)
			v = sum(map(lambda t:sum(p*q for p,q in zip(ttTable[t],tempEmission)),range(len(tagset))))
		temp[word][nextword] = v
		Lookup[word].append(findMax(temp[word]))
	except KeyError:
		Lookup[word].append([])

# Write the lookup table into a file
try:
	lut = open(sys.argv[3],'w')
	for word, val in Lookup.items():
		lut.write(word+":")
		for w in val[0]:
			lut.write(w + " ")
		lut.write(",")
		for w in val[1]:
			lut.write(w + " ")
		lut.write("\n")
	lut.close()
except IOError:
	print sys.argv[0],'couldn\'t open lookup table file',sys.argv[3],'for writing'
	sys.exit(5)

# Scoring part using perplexity
#############################################################################
# Read the train-corpus directory and put the filenames in corpusFiles
try:
        corpusFiles = [ f for f in listdir(sys.argv[2]) if isfile(join(sys.argv[2],f)) ]
except OSError:
        print sys.argv[0],'the test corpus directory doesn\'t exist'
       	sys.exit(2)
	# Check if the corpus directory is empty
if len(corpusFiles) == 0:
        print sys.argv[0],'Corpus directory is empty'
        sys.exit(3)
	# W = total #words in all the test corpuses
W = 0

compare = 0
	# Go through each of the corpus files and gather the counts
for corpus in corpusFiles:
        try:
                c = open( join(sys.argv[2],corpus), "r" )
        except IOError:
       	        print sys.argv[0],'Error: Couldn\'t read corpus file',corpus
                continue
        # Split for each word_tag combination and create a list
        corpus = c.read().strip().split(" ")
        # Close the file
        c.close()
	
	# word-based probability
	# $P(O_{1}O{2}\cdots O_{N})$ for a sentence |N|
	prob_ws = 1.0
	# For the first tag_word, we consider this as begin sentence tag_word
	bstag = corpus[0].split("_")[0]
	bsword = convertIfNeeded(corpus[0].split("_")[1],bstag)
		# Form the sentence to calculate the marginalized probability
	sentence = ['^']
	sentence.append(bsword)

	# the length of the current sentence
	N = 1
	
	# Increment the probability values
	try:
		prob_ws *= wtTable[BSW][bsword]
	except KeyError:
		prob_ws *= 0.0	#minval
	
	# Store the previous word
	prevword = bsword
	
	# Iterate over the corpus for gathering counts
	for i in range(len(corpus))[1:]:
		# Get the current tag_word
		curtag = corpus[i].split("_")[0]
		curword = convertIfNeeded(corpus[i].split("_")[1],curtag)
		sentence.append( curword )
	
		# Increase the count and the probabilties
		N += 1
			
		# Increment the probability values
		try:
			prob_ws *= wtTable[prevword][curword]
		except KeyError:
			prob_ws *= 0.0	#minval
		
		# If the current word is also a begin-sentence word
		if curtag == "PUN" and curword in ['.','?','!']:
		# At the end of each sentence, calculate the following
			# tagged-word-based probability
			# $P(O_{1}O{2}\cdots O_{N}) = $ 
			# $\sum_{S_{1}\cdots S_{N}}P(O_{1}\cdots O_{N}S_{1}\cdots S_{N})$ for a sentence |N|
			prob_tws = marginalizeOverTags( sentence )
			try:
				compare += math.log(prob_tws/prob_ws)
			except ValueError:
				try:
					compare += math.log(sys.float_info.min/prob_ws)
				except ValueError:
					None
			except ZeroDivisionError:
				try:
					compare += math.log(prob_tws/sys.float_info.min)
				except ValueError:
					None
			
			# Reinitialize the sentence
			sentence = ['^']
			# Re-initialize the probabilities
			prob_ws = 1.0
			
			# Re-initialize count
			W += N
			N = 0
			# Set previous word as bsword
			prevword = BSW
			
		else:
			# Store the current word
			prevword = curword
print math.exp(compare/W)
