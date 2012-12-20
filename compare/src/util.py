#!/usr/bin/env python
#####################
#TODO Description of this script

# Heuristic function about converting a word to lowercase
# -------------------------------------------------------
# Returns lowercase if the tag of the word is not NP0 (proper noun) 
# or PNP when the word is 'I', change its case
def convertIfNeeded( word, tag ):
        if tag == 'NP0' or (tag == 'PNP' and word == 'I' ):
                return word
        return word.lower()

# Find a list of the keys with maximum numeric values from a dictionary
def findMax( d ):
        temp = map(lambda y:(d[y],y),d)
	if len(temp) == 0:
		return ['']
	maxval = max(temp)[0]
	minval = min(temp)[0]
	# If all the values are the same
	if len(temp) > 1 and maxval == minval:
		return [''] # no guess
	return map(lambda z:z[1],filter(lambda x:x[0]== maxval and x[1] or None,temp))
#	return map(lambda z:z[1],filter(lambda x:x[0]== maxval and x[1] or None,temp))

# Find only one max 
def findOneMax( d ):
        return  max(map(lambda y:(d[y],y),d))[1]
