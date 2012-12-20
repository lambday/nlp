#!/usr/bin/env python
#####################
# This script defines the BNC tagset and forms a
# tag dictionary to be used in other scripts

# The BNC tagset
tagset = ['AJ0','AJC','AJS','AT0','AV0','AVP','AVQ',\
          'CJC','CJS','CJT','CRD','DPS','DT0','DTQ',\
          'EX0','ITJ','NN0','NN1','NN2','NP0','ORD',\
          'PNI','PNP','PNQ','PNX','POS','PRF','PRP',\
          'PUL','PUN','PUQ','PUR','TO0','UNC','VBB',\
          'VBD','VBG','VBI','VBN','VBZ','VDB','VDD',\
          'VDG','VDI','VDN','VDZ','VHB','VHD','VHG',\
          'VHI','VHN','VHZ','VM0','VVB','VVD','VVG',\
          'VVI','VVN','VVZ','XX0','ZZ0']

# form a dictionary using the tagset
tagdictionary = dict(zip(tagset,range(len(tagset))))

# BSW is short for Begin Sentence Word, we'll be creating a row for
# the words that have been used to begin a sentence
BSW = "^"
BST = len(tagset)

# Puncituation word list
PunWordList = ['.',';','?','!']

# getcounts returns the list of tag-id(s) in the ambiguity tags 
# and the count(s) to be added as a list of tuple
def getcounts( tag ):
	tmp = filter(lambda t: t if t in tagset else None,tag.split("-"))
	return map(lambda t:(tagdictionary[t],1.0/len(tmp)),tmp)

# If the current word is also a begin-sentence word
def isEndSentence( prevtag, prevword ):
	if prevtag == "PUN" and prevword in PunWordList:
		return True
	return False
