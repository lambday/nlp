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
