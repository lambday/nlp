#!/usr/bin/env python

tagset = ['tag1','tag2']
ttTable = [[0.2,0.8],[0.6,0.4],[0.1,0.9]]
twtTable = [{'word1':{'word1':0.2},"^":{'word1':0.05}},{'word1':{'word1':0.6},"^":{'word1':0.15}}]
BST = len(tagset)
print ttTable
print twtTable

def marginalizeOverTags( sentence ):
        #TODO this is also temporary, gotta rethink
        if len( sentence ) < 2:
                return 1

        # Initialize the marginal with emission probabilities
        marginal = []
        for t in range(len(tagset)):
                try:
                        marginal.append( twtTable[t][sentence[-2]][sentence[-1]] )
                except KeyError:
                        marginal.append( 0.0 )
        print 'word = ',sentence[-1],
        print 'current marginal',marginal

        # Iterate over the sentence from backwords to calculate the marginal
        for k in range(len(sentence),0,-1)[2:]:
                temp = []
                tempEmission = []
                for t in range(len(tagset)):
                        temp.append(sum(p*q for p,q in zip(ttTable[t], marginal)))
                        try:
                                tempEmission.append( twtTable[t][sentence[k-1]][sentence[k]] )
                        except KeyError:
                                tempEmission.append( 0.0 )
#               print len(tempEmission),len(temp)
                print 'word = ',sentence[k],
		print 'tempEmission',tempEmission
		print 'temp = ',temp

                marginal = map(lambda x:x[0]*x[1],zip(temp, tempEmission))
                print 'current marginal',marginal
        marginal = sum(p*q for p,q in zip(ttTable[BST], marginal))
        print marginal

        return marginal


marginalizeOverTags(['^','word1','word1','word1'])
