"""
Written for generating a lexicon for twitter sentiment
Based on a tutorial given by Christopher Potts [sentiment.christopherpotts.net/lexicons.html]

Written by Brian McMahan, Feb 26, 2012

"""

from nltk.corpus import wordnet as wn


#assumes input is an array with 2 entries, each an array of words of opposite sentiment
#these seed words are vitally important.
#example: S=[['happy', 'ecstatic', 'elated', 'excited'], ['sad', 'morose', 'depressed']] 
def propagate(S, iter):
    Sn=[]
    T=[]
    for i in range(len(S)):
        Sn.append(set())
        T.append([])
        for j in range(len(S[i])):
            #the error is stupid. it's not real. ignore it. eclipse is dumb. comment logged at 5:30 am. =)
            Sn[i] |= set(wn.synsets(S[i][j])) #@UndefinedVariable is stupid
        T[i].append(Sn[i])
        

    return _recurprop(T, iter, 0)
    

def _recurprop(T, m, depth):
    if m==depth:
        return T
    for j in range(len(T)):
        newSame = samePolarity(T[j][depth])
        otherOpposite=set()
        for k in range(len(T)):
            if k!=j:
                otherOpposite |= otherPolarity(T[k][depth])
        T[j].append(newSame | otherOpposite)
        
    return _recurprop(T, m, depth+1)

def samePolarity(synsets):
    newsynsets=set()
    for synset in synsets:
        newsynsets |= set([synset]) | set(synset.also_sees()) | set(synset.similar_tos())
        for lemma in synset.lemmas:
            for alt_lemma in (lemma.derivationally_related_forms() + lemma.pertainyms()):
                newsynsets |= set([alt_lemma.synset])
    return newsynsets
    
def otherPolarity(synsets):
    newsynsets = set()
    for synset in synsets:
        for lemma in synset.lemmas:
            for alt_lemma in lemma.antonyms():
                newsynsets |= set([alt_lemma.synset])
                
    return newsynsets
            
        
    
"""
Analyzing outputs
"""
"""
T = propagate([['happy', 'ecstatic', 'elated', 'excited'], ['sad', 'morose', 'depressed']], 5)
pos = T[0]
neg = T[1]
print "Positive"
posSet=set()
sizes=[0, 0]
for epoch in pos:
    posSet |= epoch
    print "Round %s" % pos.index(epoch)
    print "Length of set: %s" % len(epoch)
    sizes[0]+=len(epoch)
    for word in epoch:
        print word
    print ""
    
print "\n\nNegative"
negSet = set()
for epoch in neg:
    negSet |= epoch
    print "Round %s" % neg.index(epoch)
    print "Length of set: %s" % len(epoch)
    sizes[1]+=len(epoch)
    for word in epoch:
        print word
    print ""

print "Final length of supersets"
print "Positive Set: %s" % len(posSet)
print "Negative Set: %s " % len(negSet)
print "Combined sizes of individual sets"
print "Positive sets: %s" % sizes[0]
print "Negative sets: %s" % sizes[1]
"""