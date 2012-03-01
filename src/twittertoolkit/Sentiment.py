"""
One Method to rule them all, One Method to find them,
One Method to bring them all and in the darkness bind them

haha. combining all sentiment analysis into one run through with multithreading support so 500 million sentiment 
classfications become mucho fastero

written by brian mcmahan 2/27/2012
"""
import threading
import collections
import re


#from Queue import Queue
import multiprocessing
import Queue
from time import sleep, time
import string

from nltk import word_tokenize, wordpunct_tokenize, regexp_tokenize

lexicon = None
finishedQ =  multiprocessing.Queue(100000)
tweetQ = multiprocessing.Queue(100000)
sentinelQ = multiprocessing.Queue(7)
POS = "positive"
NEG = "negative"


twitterFiles = ["tweets2009-06.txt","tweets2009-07.txt","tweets2009-08.txt","tweets2009-09.txt","tweets2009-10.txt","tweets2009-11.txt","tweets2009-12.txt"]
twitterFilepath = "/media/Media/tweets/bigdata/"

            
class TweetThread(multiprocessing.Process):
    def __init__(self, fileHandler):
        multiprocessing.Process.__init__(self)
        self.fileHandler = fileHandler

    
    def run(self):
        global sentinelQ, lexicon, POS, NEG
        search = re.search
        r = string.replace
        s = string.split
        fh = self.fileHandler.readline
        line = fh()
        pos = lexicon[POS]
        neg = lexicon[NEG]
        print line
        while line:
        #for x in range(1000000):
            if line[0]=="T":
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                fh()
                line = fh()
                tweet_str = r(r(line,"W\t",""),"\n","")
                if search('http|www', tweet_str): continue
                pcP=0
                pcN=0
                #print tweet_str
                for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                    if w in pos:
                        pcP+=1
                    if w in neg:
                        pcN+=1
                finishedQ.put([date, pcP, pcN], 1)
            line = fh()
        self.fileHandler.close()
        sentinelQ.put("DONE")
        


class SimpleProgress:
    def __init__(self, total):
        self.total = total
    
    def start(self):
        self.start = time()
        
    def update(self, x):
        elapsed = time()-self.start
        percDone = x*100.0/self.total
        estimatedTimeInSec=(elapsed*1.0/x)*self.total
        return "%s %s percent\n%s Processed\nElapsed time: %s\nEstimated time: %s\n--------" % (self.bar(percDone), round(percDone, 2), x, self.form(elapsed), self.form(estimatedTimeInSec))
        
    def form(self, t):
        hour = int(t/(60.0*60.0))
        minute = int(t/60.0 - hour*60)
        sec = int(t-minute*60-hour*3600)
        return "%s Hours, %s Minutes, %s Seconds" % (hour, minute, sec)
        
    def bar(self, perc):
        done = int(round(30*(perc/100.0)))
        left = 30-done
        return "[%s%s]" % ('|'*done, ':'*left)
        
class Sentiment:
    def __init__(self):   
        global lexicon
        ofl = OFLexicon()
        l=ofl.parseLexicon()
        self.POS = "positive"
        self.NEG = "negative"
        lexicon = {self.POS:l[0], self.NEG:l[1]}
        self.dayCounts = {}
    
    
    def perfRun(self):
        global lexicon, POS, NEG
        r=[]
        x=0
        membershipTester = set()
        prog = SimpleProgress(476553560)
        fileHandler = open("%s%s" % (twitterFilepath, twitterFiles[0]))
        r = string.replace
        s = string.split
        fh = fileHandler.readline
        line = fh()
        pos = lexicon[POS]
        neg = lexicon[NEG]
        print line
        #while line:
        for x in range(1000000):
            if line[0]=="T":
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                fh()
                tweet_str = r(r(fh(),"W\t",""),"\n","")
                pcP=0
                pcN=0
                #print tweet_str
                for w in word_tokenize(tweet_str):
                    if w in pos:
                        pcP+=1
                    if w in neg:
                        pcN+=1
        
                if date not in membershipTester:
                    membershipTester |= set([date])    
                    self.dayCounts[date] = [0,0]
                self.dayCounts[date][0]+=pcP
                self.dayCounts[date][1]+=pcN  
                if x%50000==0:
                    print prog.update(x)
                    print "days seen: %s" % len(membershipTester)
            line = fh()
    
    def word_tokenizeTesting(self):
        fileHandler = open("%s%s" % (twitterFilepath, twitterFiles[0]))
        r = string.replace
        s = string.split
        fh = fileHandler.readline
        line = fh()
        print line
        #while line:
        for x in range(1000):
            if line[0]=="T":
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                fh()
                tweet_str = r(r(fh(),"W\t",""),"\n","")
                word_tokenize(tweet_str)
            line = fh()
            
    def regexp_tokenizeTesting(self):
        fileHandler = open("%s%s" % (twitterFilepath, twitterFiles[0]))
        r = string.replace
        s = string.split
        fh = fileHandler.readline
        line = fh()
        print line
        #while line:
        for x in range(1000):
            if line[0]=="T":
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                fh()
                tweet_str = r(r(fh(),"W\t",""),"\n","")
                regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+')
            line = fh()
    
    def tester(self):
        import timeit
        print "Word Tokenize:"
        print "%s" % timeit(self.word_tokenizeTesting())
        print "RegExp Tokenize:"
        print "%s" % timeit(self.regexp_tokenizeTesting())
    
    def run(self):
        global finishedQ, sentinelQ, tweetQ
        r=[]
        x=0
        membershipTester = set()
        prog = SimpleProgress(476553560)
        for f in twitterFiles:
            print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetThread = TweetThread(fileHandler)
            tweetThread.start()
            r.append(tweetThread)
            
        prog.start()
            

        while (not sentinelQ.full()) or (not finishedQ.empty()):
            x+=1
            [day, pos, neg] = finishedQ.get(1)
            if day not in membershipTester:
                membershipTester |= set([day])    
                self.dayCounts[day] = [0,0]
            self.dayCounts[day][0]+=pos
            self.dayCounts[day][1]+=neg  
            if x%50000==0:
                print prog.update(x)
                #print "at %s" % x
                print "finishedQ: %s" % finishedQ.qsize()
                print "sentinelQ: %s\n\n-----\n" % sentinelQ.qsize()
                    
            
        print "Done with all threads, printing results to a file"
        filepath = "/home/brian/TwitterSpring2012/RUTA/data/OFLexicon.results.httpwwwsimplefilter"
        fh = open(filepath, 'w')
        sortedKeys = self.dayCounts.keys()
        sortedKeys.sort()
        for day in sortedKeys:
            r = "%s,%s,%s\n" % (day, self.dayCounts[day][0], self.dayCounts[day][1])
            print r
            fh.write(r)
        fh.close()
        print "Finito"
        


baseDir = "/home/brian/TwitterSpring2012/RUTA/"

filepath="data/opinionfinder.lexicon.originalformat.tff"

class OFLexicon:
    def parseLexicon(self):
        fh = open(baseDir+filepath)
        d = dict()
        line = fh.readline()
        x=0
        while (line):
            x+=1
            [polarity, sent] = self.parseline(line)
            if polarity not in d:
                d[polarity] = set()
            d[polarity] |= set([sent])
            line = fh.readline()
    
        return [d["positive"] | d["both"], (d["negative"] | d["weakneg"] | d["both"])]
        
    def parseline(self, line):
        x=self.todict(word_tokenize(line))
        return [x["priorpolarity"], sentiment(x["word1"], x["type"], x["pos1"], x["priorpolarity"])]
        
    def todict(self, tokens):
        d=dict()
        for y in range(len(tokens)):
            if tokens[y]=="=" and y!=0 and y!=len(tokens):
                d[tokens[y-1]]=tokens[y+1]
        return d
    
class sentiment:
    def __init__(self, lemma, wordtype, pos, polarity):        
        self.lemma = lemma
        self.wordtype = wordtype
        self.pos = pos
        self.polarity=polarity
    
    def __str__(self):
        return "sentiment(lemma=%s, polarity=%s, pos=%s)" % (self.lemma, self.polarity, self.pos)
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash(self.lemma)
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.lemma==other
        if other.lemma==self.lemma and other.pos==self.pos:
            return True
        return False


#S=Sentiment()
#S.run()
