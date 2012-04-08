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
SPOS = "strongsubj-positive"
SNEG = "strongsubj-negative"
SNEU = "strongsubj-neutral"
WPOS = "weaksubj-positive"
WNEG = "weaksubj-negative"
WNEU = "weaksubj-neutral"


twitterFiles = ["tweets2009-06.txt","tweets2009-07.txt","tweets2009-08.txt","tweets2009-09.txt","tweets2009-10.txt","tweets2009-11.txt","tweets2009-12.txt"]
twitterFilepath = "/media/Media/tweets/bigdata/"

            
class TweetProcess(multiprocessing.Process):
    def __init__(self, fileHandler, fp):
        multiprocessing.Process.__init__(self)
        self.fileHandler = fileHandler
        self.fp = fp
        self.ret="Not a set yet"
    
    def run(self):
        #self.eightconditionrun()
        self.userCountRun()
        
    def userCountRun(self):
        r = string.replace
        fh = self.fileHandler.readline
        
        lc = string.lower
        search = re.search
        s = string.split
        line = fh()
        userDict=set()
        print line
        #while line:
        for x in range(10000000):
            if line[0]=="T":
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                user=r(r(fh(), "U\thttp://twitter.com/",""), "\n", "")
                tweet_str = lc(r(r(line,"W\t",""),"\n",""))
                if search('RT', tweet_str):
                    print user, tweet_str
            line=fh()
        self.ret = userDict
        
    def getUsers(self):
        print self.ret
        return self.ret
            
    def eightconditionrun(self):
        global sentinelQ, lexicon, WPOS, WNEG, SPOS, SNEG, SNEU, PNEU
        #op = open("/home/brian/TwitterSpring2012/RUTA/data/%s.testview" % self.fp, 'a')
        search = re.search
        r = string.replace
        s = string.split
        lc = string.lower
        fh = self.fileHandler.readline
        line = fh()
        wpos = lexicon[WPOS]
        wneg = lexicon[WNEG]
        wneu = lexicon[WNEU]
        spos = lexicon[SPOS]
        sneg = lexicon[SNEG]
        sneu = lexicon[SNEU]
        print line
        while line:
        #for x in range(100000):
            if line[0]=="T":
                retter=False
                date = s(r(r(line, "T\t", ""), "\n", ""))[0]
                fh() # user read here and discarded
                line = fh()
                tweet_str = r(r(line,"W\t",""),"\n","")
                if search('http|www', tweet_str): continue
                numPos=[0,0]
                numNeg=[0,0]
                numNeu=[0,0]
                #print tweet_str
                for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                    w=lc(w)
                    if w in spos: numPos[0]+=1; retter=True
                    elif w in wpos: numPos[1]+=1; retter=True
                    elif w in sneg: numNeg[0]+=1; retter=True
                    elif w in wneg: numNeg[1]+=1; retter=True
                    elif w in sneu: numNeu[0]+=1; retter=True
                    elif w in wneu: numNeu[1]+=1; retter=True
                if retter:
                    #op.write("Tweet\n%s\nSentiment: %s, %s\n\n" % (tweet_str, pcP, pcN))
                    finishedQ.put([date, [numPos, numNeg, numNeu]], 1)
            line = fh()
        #op.close()
        print("This file is done: %s" % self.fp)
        self.fileHandler.close()
        sentinelQ.put("DONE")
        print "SentinelQ: %s, finishedQ: %s" % (sentinelQ.qsize(), finishedQ.qsize())
        


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
        global lexicon, WPOS, WNEG, SPOS, SNEG, SNEU, WNEU
        ofl = OFLexicon()
        l=ofl.parseLexicon()
        lexicon = {SPOS:l[0], WPOS:l[1], SNEG:l[2], WNEG:l[3], SNEU:l[4], WNEU:l[5]}
        self.castedDayCounts = {True: {}, False: {}}
        self.uncastedDayCounts = {True: {}, False: {}}
        self.castedNeutralCounts = {True: {}, False: {}}
        self.uncastedNeutralCounts = {True: {}, False: {}}
    
    
    def run(self):
        #self.eightconditionrun()
        self.userCountRun()
    
    def userCountRun(self):
        users=set()
        processes=collections.deque()
        finished=[]
        for f in twitterFiles:
            #print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetThread = TweetProcess(fileHandler, f)
            tweetThread.start()
            processes.append(tweetThread)
        while len(processes)>0:
            p=processes.popleft()
            if p.is_alive():
                processes.append(p)
            else:
                print "Finishing a thread"
        
    
    def eightconditionrun(self):
        global finishedQ, sentinelQ, tweetQ
        r=[]
        x=0
        membershipTester = set()
        prog = SimpleProgress(476553560)
        for f in twitterFiles:
            print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetThread = TweetProcess(fileHandler, f)
            tweetThread.start()
            r.append(tweetThread)
            
        prog.start()
            

        while (not sentinelQ.full()) or (not finishedQ.empty()):
            x+=1
            try:
                [day, [[spos, wpos], [sneg, wneg], [sneu, wneu]]] = finishedQ.get(1, 5)
                if day not in membershipTester:
                    membershipTester |= set([day])    
                    self.castedDayCounts[True][day]=[0,0] # cast and weighted
                    self.castedDayCounts[False][day]=[0,0] # cast and not weighted
                    self.uncastedDayCounts[True][day]=[0,0] # uncast and weighted
                    self.uncastedDayCounts[False][day]=[0,0] # uncast and not weighted
                    self.castedNeutralCounts[True][day]=[0,0,0] # same pattern as above
                    self.castedNeutralCounts[False][day]=[0,0,0]
                    self.uncastedNeutralCounts[True][day]=[0,0,0]
                    self.uncastedNeutralCounts[False][day]=[0,0,0]
                #weighted and uncast
                self.uncastedDayCounts[True][day][0]+=spos+wpos*0.5
                self.uncastedDayCounts[True][day][1]+=sneg+wneg*0.5
                self.uncastedNeutralCounts[True][day][0]+=spos+wpos*0.5
                self.uncastedNeutralCounts[True][day][1]+=sneg+wneg*0.5
                self.uncastedNeutralCounts[True][day][2]+=sneu+wneu*0.5
                #not weighted and uncast
                self.uncastedDayCounts[False][day][0]+=spos+wpos
                self.uncastedDayCounts[False][day][1]+=sneg+wneg
                self.uncastedNeutralCounts[False][day][0]+=spos+wpos
                self.uncastedNeutralCounts[False][day][1]+=sneg+wneg
                self.uncastedNeutralCounts[False][day][2]+=sneu+wneu
                
                #cases for cast and weighted
                if spos+wpos*0.5>=sneg+wneg*0.5:
                    self.castedDayCounts[True][day][0]+=1 #weighted, cast
                    if spos+wpos*0.5>=sneu+wneu*0.5: #cases for ternary, weighted, cast
                        self.castedNeutralCounts[True][day][0]+=1
                    else:
                        self.castedNeutralCounts[True][day][2]+=1
                else:
                    self.castedDayCounts[True][day][1]+=1 #weighted, cast
                    if sneg+wneg*0.5>=sneu+wneu*0.5: #caes for ternary, weighted, cast
                        self.castedNeutralCounts[True][day][1]+=1
                    else:
                        self.castedNeutralCounts[True][day][2]+=1
                
                #cases for unweighted and cast
                if spos+wpos>=sneg+wneg:
                    self.castedDayCounts[False][day][0]+=1 # unweighted, cast
                    if spos+wpos>=sneu+wneu: #cases for ternary
                        self.castedNeutralCounts[False][day][0]+=1
                    else:
                        self.castedNeutralCounts[False][day][2]+=1
                else:
                    self.castedDayCounts[False][day][1]+=1 #unweighted, cast
                    if sneg+wneg>=sneu+wneu: #cases for ternary
                        self.castedNeutralCounts[False][day][1]+=1
                    else:
                        self.castedNeutralCounts[False][day][2]+=1


            
            
            except:
                print "Catching Exception"
            if x%50000==0:
                print prog.update(x)
                #print "at %s" % x
                print "finishedQ: %s" % finishedQ.qsize()
                print "sentinelQ: %s\n\n-----\n" % sentinelQ.qsize()
                    
            
        print "Done with all threads, printing results to a file"
        extensions = ["cast.weighted.noneutral", "cast.notweighted.nonetural", "cast.weighted.withneutral", "cast.notweighted.withneutral", "notcast.weighted.noneutral", "notcast.notweighted.nonetural", "notcast.weighted.withneutral", "notcast.notweighted.withneutral"]
        filepath = "/home/brian/TwitterSpring2012/RUTA/data/OFLexicon.results."
        fh=[]
        for r in extensions:
            fh.append(open("%s%s" % (filepath, r), 'w'))
        sortedKeys = self.castedDayCounts[True].keys()
        sortedKeys.sort()
        for day in sortedKeys:
            #r = "%s,%s,%s\n" % (day, self.dayCounts[day][0], self.dayCounts[day][1])
            #cast, no neutral, weighted
            fh[0].write("%s,%s,%s\n" % (day, self.castedDayCounts[True][day][0], self.castedDayCounts[True][day][1]))
            #cast, no neutral, not weighted
            fh[1].write("%s,%s,%s\n" % (day, self.castedDayCounts[False][day][0], self.castedDayCounts[False][day][1]))
            #cast, neutral, weighted
            fh[2].write("%s,%s,%s,%s\n" % (day, self.castedNeutralCounts[True][day][0], self.castedNeutralCounts[True][day][1],self.castedNeutralCounts[True][day][2]))
            #cast, neutral, not weighted
            fh[3].write("%s,%s,%s,%s\n" % (day, self.castedNeutralCounts[False][day][0], self.castedNeutralCounts[False][day][1],self.castedNeutralCounts[False][day][2]))
            #not cast, no neutral, weighted
            fh[4].write("%s,%s,%s\n" % (day, self.uncastedDayCounts[True][day][0], self.uncastedDayCounts[True][day][1]))
            #not cast, no neutral, not weighted
            fh[5].write("%s,%s,%s\n" % (day, self.uncastedDayCounts[False][day][0], self.uncastedDayCounts[False][day][1]))
            #not cast, neutral, weighted
            fh[6].write("%s,%s,%s,%s\n" % (day, self.uncastedNeutralCounts[True][day][0], self.uncastedNeutralCounts[True][day][1],self.uncastedNeutralCounts[True][day][2]))
            #not cast, neutral, not weighted
            fh[7].write("%s,%s,%s,%s\n" % (day, self.uncastedNeutralCounts[False][day][0], self.uncastedNeutralCounts[False][day][1],self.uncastedNeutralCounts[False][day][2]))
            #fh.write(r)
        for handler in fh:
            handler.close()

#        for day in self.castedDayCounts[True]:
#            print "Day: %s" % day
#            print "Cast, Weighted: %s, ratio: %s\n" % (self.castedDayCounts[True][day], self.castedDayCounts[True][day][0]*1.0/(1+self.castedDayCounts[True][day][1]))
#            print "Cast, not weighted: %s, ratio: %s\n" % (self.castedDayCounts[False][day], self.castedDayCounts[False][day][0]*1.0/(1+self.castedDayCounts[False][day][1]))
#            print "Cast, With Neutral, Weighted: %s, ratio: %s\n" % (self.castedNeutralCounts[True][day], self.castedNeutralCounts[True][day][0]*1.0/(1+self.castedNeutralCounts[True][day][1]))
#            print "Cast, with neutral, no weighted: %s, ratio: %s\n" % (self.castedNeutralCounts[False][day], self.castedNeutralCounts[False][day][0]*1.0/(1+self.castedNeutralCounts[False][day][1]))
#            print "uncast, weighted: %s, ratio: %s\n" % (self.uncastedDayCounts[True][day], self.uncastedDayCounts[True][day][0]*1.0/(1+self.uncastedDayCounts[True][day][1]))
#            print "uncast, not weighted: %s, ratio: %s\n" % (self.uncastedDayCounts[False][day], self.uncastedDayCounts[False][day][0]*1.0/(1+self.uncastedDayCounts[False][day][1]))
#            print "uncast, with neutral, weighted: %s, ratio: %s\n" % (self.uncastedNeutralCounts[True][day], self.uncastedNeutralCounts[True][day][0]*1.0/(1+self.uncastedNeutralCounts[True][day][1]))
#            print "uncast, with neutral, not weighted: %s, ratio: %s\n" % (self.uncastedNeutralCounts[False][day], self.uncastedNeutralCounts[False][day][0]*1.0/(1+self.uncastedNeutralCounts[False][day][1]))
#            print "\n\n"
        print "Finito"
    
    def oldrun(self):
        global finishedQ, sentinelQ, tweetQ
        r=[]
        x=0
        membershipTester = set()
        prog = SimpleProgress(476553560)
        for f in twitterFiles:
            print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetThread = TweetProcess(fileHandler, f)
            tweetThread.start()
            r.append(tweetThread)
            
        prog.start()
            

        while (not sentinelQ.full()) or (not finishedQ.empty()):
            x+=1
            try:
                [day, sent, pos, neg] = finishedQ.get(1, 5)
                if day not in membershipTester:
                    membershipTester |= set([day])    
                    self.dayCounts[day] = [0,0]
                    self.otherDayCounts[day]= [0, 0]
                self.otherDayCounts[day][0]+=pos
                self.otherDayCounts[day][1]+=neg
                if sent:
                    self.dayCounts[day][0]+=1
                else:
                    self.dayCounts[day][1]+=1
            except:
                for day in self.dayCounts:
                    print day, self.dayCounts[day], self.dayCounts[day][0]*1.0/self.dayCounts[day][1]
                    print day, self.otherDayCounts[day], self.otherDayCounts[day][0]*1.0/self.otherDayCounts[day][1]
#            if x%50000==0:
#                print prog.update(x)
#                #print "at %s" % x
#                print "finishedQ: %s" % finishedQ.qsize()
#                print "sentinelQ: %s\n\n-----\n" % sentinelQ.qsize()
                    
            
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

        for day in self.dayCounts:
            r=self.dayCounts[day][0]*1.0/self.dayCounts[day][1]
            s = self.otherDayCounts[day][0]*1.0/self.otherDayCounts[day][1]
            print day, self.dayCounts[day]
            print day, self.otherDayCounts[day]
            print r/s
            print
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
    
        return [d["strongsubj-positive"], d["weaksubj-positive"], d["strongsubj-negative"], d["weaksubj-negative"], d["strongsubj-neutral"], d["weaksubj-neutral"]]
        
    def parseline(self, line):
        x=self.todict(word_tokenize(line))
        return ["%s-%s" % (x['type'], x["priorpolarity"]), sentiment(x["word1"], x["type"], x["pos1"], x["priorpolarity"])]
        
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


S=Sentiment()
S.run()
