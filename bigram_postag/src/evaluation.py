#!/usr/bin/env python
# creates confusion matrix and tag-wise accuracy

import sys
from bnc import tagset, tagdictionary

if len(sys.argv) < 3:
	print 'Usage:',sys.argv[0],'<original-corpus> <tagged-corpus>'
	sys.exit(1)
try:
	org = open( sys.argv[1], "r" )
	tag = open( sys.argv[2], "r" )
except IOError:
	print sys.argv[0],'couldn\'t not read the input files'
	sys.exit(2)

# read just the taglists
org_taglist = map(lambda x:x.split("_")[0],org.read().strip().split(" "))
tag_taglist = map(lambda x:x.split("_")[0],tag.read().strip().split(" "))

# if the length of the taglists are different, raise an error
if len(org_taglist) != len(tag_taglist):
	print sys.argv[0],'the tagged corpus is not',sys.argv[2]
	sys.exit(3)

# create the confusion matrix, A[i,j] where tag i is classified as taj j
confusionMatrix = []
for i in range(len(tagset)):
	confusionMatrix.append([0] * len(tagset))

#print org_taglist
#print tag_taglist

# run through the taglists and fill the confusion matrix
for i in range(len(org_taglist)):
	t_tag = tagdictionary[tag_taglist[i]]
	try:
		o_tag = tagdictionary[org_taglist[i]]
		confusionMatrix[o_tag][t_tag] += 1
	except KeyError:
		# probably an ambiguity tag has encountered. In this case, if the
		# predicted tag is any one of the ambiguity tags, take that as correct
		o_tag1 = tagdictionary[org_taglist[i].split("-")[0]]
		o_tag2 = tagdictionary[org_taglist[i].split("-")[1]]
		if o_tag1 == t_tag:
			confusionMatrix[o_tag1][t_tag] += 1
		elif o_tag2 == t_tag:
			confusionMatrix[o_tag2][t_tag] += 1
		else: # however, if it does not match with any of these, then we fill up for both
			confusionMatrix[o_tag1][t_tag] += 1
			confusionMatrix[o_tag2][t_tag] += 1



# print the confusion matrix in a file
name = reduce(lambda x,y:x+'.'+y,sys.argv[1].split(".")[:-1]) + "_cnf.csv" #+ sys.argv[1].split(".")[-1]
cnf = open( name, "w" )
for i in range(len(tagset)):
	for j in range(len(tagset)):
		cnf.write(str(confusionMatrix[i][j])+",")
	cnf.write("\n")

