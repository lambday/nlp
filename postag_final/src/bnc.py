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

# getcounts returns the list of tag-id(s) in the ambiguity tags 
# and the count(s) to be added as a list of tuple
def getcounts( tag ):
	tmp = filter(lambda t: t if t in tagset else None,tag.split("-"))
	return map(lambda t:(tagdictionary[t],1.0/len(tmp)),tmp)

# If the current word is also a begin-sentence word
def isEndSentence( prevtag, prevword ):
	if prevtag == "PUN" and prevword in ['.','?','!',';']:
		return True
	return False

# Common suffix list
# source: http://www.englishlanguageterminology.org/definition-of-words/list-of-suffixes.htm
suffix = ["able","ad","ade","age","agogy","al","ality","an","ance","ancy",\
        "ant","ar","ard","ary","arch","archy","ate","athlon","ation","ative",\
        "atory","bound","cide","city","cy","cycle","dom","ectomy","ed","ee",\
        "eer","eme","en","ence","ency","ent","eous","er","ergy","ern","ery",\
        "ese","esque","ess","etic","fare","ful","gon","gry","holic","hood","ia",\
        "iable","ial","ian","iant","iate","ible","ibly","ic","ical","ics","id",\
        "ier","ify","ile","illion","ious","ing","ion","ish","ism","ist","ite",\
        "itive","itude","ity","ium","ive","ization","isation","ize","ise","land",\
        "less","like","ling","ly","man","ment","meter","metry","mony","most",\
        "nesia","ness","ocracy","ography","ologist","ology","onomy","or","ory",\
        "ose","ous","phone","scope","ship","shire","sion","some","ster","t","th",\
        "tion","ty","uary","ulent","ward","wise","wright","y"]
