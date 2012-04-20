import cPickle as pickle
import os
from math import log
from time import time

import re

def getCountin(origDict, words, fHandles):   
    for wrd in words:
        origDict[wrd] = {'__count':0}
    origDict['T'] = {'__count':0}

    original = set(words)

    pattern = re.compile(r"[^a-z]")
    for fh in fHandles:
        print fh,

        st = time()
        lines = fh.readlines()
        for line in lines:
            origDict['T']['__count'] += 1
            toks = line.lower().split()
            freq = float(toks[-1])
            for tok in toks[:-1]:
                if tok in original:
                    origDict[tok]['__count'] += freq
                    for tk in toks:
                        if tk != tok and not pattern.search(tk):
                            if tk in origDict[tok]:
                                origDict[tok][tk] += freq
                            else:
                                origDict[tok][tk] = freq
        print time()-st
    return origDict
    
if __name__ == "__main__":

    original = [# TENSION
                'tense', 'shaky', 'on-edge', 'panicky', 'uneasy', 'restless',
                'nervous', 'anxious', 'relaxed',
                # DEPRESSION
                'unhappy', 'sorry-for-things-done', 'sad', 'blue', 'hopeless',
                'unworthy', 'discouraged', 'lonely', 'miserable', 'gloomy',
                'desperate', 'helpless', 'worthless', 'terrified', 'guilty',
                # ANGER
                'anger', 'peeved', 'grouchy', 'spiteful', 'annoyed', 'resentful',
                'bitter', 'ready-to-fight','rebellious', 'deceived', 'furious',
                'bad-tempered',
                # VIGOUR
                'lively', 'active', 'energetic', 'cheerful', 'alert',
                'full of pep', 'carefree', 'vigorous',
                # FATIGUE
                'worn-out', 'listless', 'fatigued', 'exhausted', 'sluggish',
                'weary', 'bushed',
                # CONFUSION
                'confused', 'unable-to-concentrate', 'muddled', 'bewildered',
                'forgetful', 'uncertain-about-things', 'efficient'
                ]

    frFiles = os.listdir("./4-gram/")
    fvFiles = os.listdir("./5-gram/")

    allFiles = []
    for f in frFiles:
        allFiles.append("./4-gram/"+f)
    for f in fvFiles:
        allFiles.append("./5-gram/"+f)

    frFhs = []
    for fl in frFiles:
        frFhs.append(open("./4-gram/"+fl))
 
    fvFhs = []
    for fl in fvFiles:
        fvFhs.append(open("./5-gram/"+fl))

    fhdls = frFhs + fvFhs

    countDict = getCountin({}, original, fhdls)
    
    for fh in fhdls:
        fh.close()

    fh = open("countDict.pkl", "wb")
    pickle.dump(countDict, fh)
    fh.close()
    

##    countDict = pickle.load(open("countDict.pkl", "rb"))
    otherWords = set()
    
    for key,val in countDict.iteritems():
        if key != "T":
            otherWords.add(key)
        print key, "count: ", countDict[key]["__count"], "count(other words): ", len(countDict[key].items())-1
        for k,v in countDict[key].iteritems():
            if k != "__count":
                otherWords.add(k)
                #print k

            
    print len(otherWords)

    f = open("./Unigram/vocab")
    unigramCounts = {}

    st = time()
    count = 0
    while True:
        lines = f.readlines(1000000)
        if not lines:
            break

        for line in lines:
            word,freq = line.lower().split()
            freq = float(freq)
            if word in otherWords:
                unigramCounts[word] = freq

        count += 1000000
        print count, time()-st
    f.close()

    f = open("neighborhoods.csv", "w")
    for key,val in countDict.iteritems():
        if key != "T":
            for k,v in countDict[key].iteritems():
                if k != "__count" and not re.search(r"[^a-z]", k):
                    #print k,(k in otherWords)
                    #print countDict['T']['__count'], v, unigramCounts[key], unigramCounts[k]
                    coocMetric = countDict['T']['__count']*v*1.0/(unigramCounts[key]*unigramCounts[k])
                    f.write(key+","+k+",")
                    f.write(str(countDict['T']['__count'])+","+str(v)+",")
                    f.write(str(unigramCounts[key])+","+str(unigramCounts[k])+",")
                    f.write(str(countDict['T']['__count']*v*1.0/(unigramCounts[key]*unigramCounts[k])))
                    if coocMetric != 0:
                        f.write(","+str(log(coocMetric,2))+"\n")
                    else:
                        f.write(",0\n")
    f.close()