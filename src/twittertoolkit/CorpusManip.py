"""
This file is mainly the preprocessing steps taken on the corpus
Among them:

Split corpus into seperate time instances (days)
Calculate the dictionary for LDA by finding the top 1000 tf*idf terms per day and then merging the sets
Replacing the tweets with LDA document form: UNIQUE_WORD_COUNT WORD1:NUMBER_OF_OCCURENCES ... WORD_UNIQUE_WORD_COUNT:NUMBER_OF_OCCURENCES

I think that's it

written by brian mcmahan over a span from 2/27/2012 - current date (4/4/2012)
"""
import threading
import collections
import re
import math
from operator import itemgetter

#from Queue import Queue
import multiprocessing
from Queue import Empty
from time import time
import string
import commands
from nltk import regexp_tokenize

finishedQ =  multiprocessing.Queue(100000)
sentinelQ = multiprocessing.Queue(7)
fileQ = multiprocessing.Queue(214)


corpusDictFile = open("/home/brian/TwitterSpring2012/RUTA/data/allWords.final", 'r')
corpusDictionary = []
fl = corpusDictFile.readline
line = fl() #purposely starting from one in the dict.. the first line of the file is a summary line
while line:
    corpusDictionary.append(string.replace(line, "\n", ""))
    line = fl()
corpusDictFile.close()
corpusSet = set(corpusDictionary)
corpusDict = dict()
for x in range(len(corpusDictionary)):
    corpusDict[corpusDictionary[x]] = x


twitterFiles = ["tweets2009-06.txt","tweets2009-07.txt","tweets2009-08.txt","tweets2009-09.txt","tweets2009-10.txt","tweets2009-11.txt","tweets2009-12.txt"]
twitterFilepath = "/media/Media/tweets/bigdata/"
opfp = "/media/OS/twitterdata/"
            
class TweetProcess(multiprocessing.Process):
    def __init__(self, filePaths):
        multiprocessing.Process.__init__(self)
#        self.fileHandler = fileHandler
#        self.fp = fp
#        self.ret="Not a set yet"
        self.filePaths = filePaths
    
    def run(self):
        #self.splitCorpus()
        #self.preprocessCorpus()
        #self.singleDayProcessing()
        self.singleDayToWordNumbers()

    def singleDayToWordNumbers(self):
        global finishedQ, sentinelQ, corpusSet, corpusDict
        paths = self.filePaths
        r = string.replace
        s = string.split
        lc = string.lower
        log = math.log
        #.count the frequency of each word
        #.weight each frequency by its idf (inverse doc frequency.  log(totalDocs/#DocsWordAppears)
        #.take the top 1000
        #.output to a file AND report back the set so we can merge
        while len(paths)>0:
            try:
                someFilePath = paths.pop()
                print "Starting %s" % someFilePath
                handler = open(someFilePath, 'r')
                writehandler = open("%s.converted" % someFilePath, 'w')
                fh = handler.readline
                wh = writehandler.write
                line = fh()
                totalDocs = 0
                reducedDocs = 0
                words = {}
                wordsSet = set()
                while line:
                    if line[0]=="T":
                        totalDocs+=1
                        user = fh()
                        thisDoc = set()
                        thisDocFinal = dict()
                        tweet_str = lc(r(r(fh(),"W",""),"\n",""))
                        for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                            if w in corpusSet:
                                if w not in thisDoc:
                                    thisDocFinal[corpusDict[w]]=0
                                    thisDoc |= set([w])
                                thisDocFinal[corpusDict[w]]+=1
                        if len(thisDocFinal)>0:   
                            reducedDocs+=1
                            outputter = "%s" % len(thisDocFinal)
                            for w in thisDocFinal:
                                outputter+=" %s:%s" % (w, thisDocFinal[w])
                            outputter+="\n"
                            wh(outputter)
                        
                    line = fh()
                filestats = open("%s.stats" % someFilePath, 'w')
                filestats.write("totalDocs,%s" % reducedDocs)
                filestats.close()        
                handler.close()
                writehandler.close()
                finishedQ.put("dummy", 1)
                print "Just finished %s" % someFilePath               
            except Empty:
                print "Tweet process seeing empty fileQ"
        sentinelQ.put("DONE")
        print "SentinelQ: %s, finishedQ: %s, fileQ: %s" % (sentinelQ.qsize(), finishedQ.qsize(), fileQ.qsize())

    
    def singleDayProcessing(self):
        global finishedQ, fileQ, stopwords
        paths = self.filePaths
        stopwordSet = set(stopwords)
        r = string.replace
        s = string.split
        lc = string.lower
        log = math.log
        #.count the frequency of each word
        #.weight each frequency by its idf (inverse doc frequency.  log(totalDocs/#DocsWordAppears)
        #.take the top 1000
        #.output to a file AND report back the set so we can merge
        while len(paths)>0:
            try:
                someFilePath = paths.pop()
                print "Starting %s" % someFilePath
                handler = open(someFilePath, 'r')
                fh = handler.readline
                line = fh()
                totalDocs = 0
                words = {}
                wordsSet = set()
                while line:
                    if line[0]=="T":
                        totalDocs+=1
                        user = fh()
                        thisDoc = set()
                        tweet_str = lc(r(r(fh(),"W",""),"\n",""))
                        for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                            if w in stopwordSet:
                                continue
                            if w not in wordsSet:
                                words[w] = [0,0]
                                wordsSet |= set([w])
                            if w not in thisDoc:
                                thisDoc |= set([w])
                                words[w][1]+=1
                            words[w][0]+=1
                        if totalDocs%10000==0:
                            print "Seen %s docs for %s" % (totalDocs,someFilePath)
                        #read in words
                        #parse out dictionary and counts
                        #we want to calculate the tf*idf for each word term
                    line = fh()
                handler.close()
                for w in words:
                    words[w] = words[w][0]*log(totalDocs*1.0/words[w][1])
                topWords = sorted(words.iteritems(), key=itemgetter(1), reverse=True)
                if len(topWords)>1000:
                    topWords=topWords[:1000]
                else:
                    topWords=topWords[:len(topWords)*7/10]
                outputWords = open("%s.words" % someFilePath, 'w')
                outputWords.write("totalTweets,%s\n" % totalDocs)
                output = []
                for word in topWords:
                    outputWords.write(("%s\n" % word[0]))
                    output.append(word[0])
                outputWords.close()
                topWords=None
                finishedQ.put(set(output), 1)
                print "Just finished %s" % someFilePath
                
            except Empty:
                print "Tweet process seeing empty fileQ"
        sentinelQ.put("DONE")
        print "SentinelQ: %s, finishedQ: %s, fileQ: %s" % (sentinelQ.qsize(), finishedQ.qsize(), fileQ.qsize())
            
    
#    def splitCorpus(self):
#        global sentinelQ, finishedQ, opfp
#        search = re.search
#        #validmo = set(['06', '07', '08', '09', '10', '11', '12'])
#        r = string.replace
#        s = string.split
#        lc = string.lower
#        fh = self.fileHandler.readline
#        line = fh()
#        print line
#        while line:
#        #for x in range(500000):
#            if line[0]=="T":
#                rt=False
##                wholedate = line
##                wholeuser = fh()
##                wholetweet = fh()
##                date = s(s(r(r(line, "T\t", ""), "\n", ""))[0], '-')
##                if date[0]!="2009" or date[1] not in validmo:
##                    fp = "%s%s" % (opfp, "junktweets")
##                else:
##                    fp = "%s%s/%s" % (opfp, date[1], date[2])
##                finishedQ.put([[wholedate, wholeuser, wholetweet], fp], 1)
#                user=r(r(fh(), "U\thttp://twitter.com/",""), "\n", "")
#                tweet_str = lc(r(r(fh(),"W",""),"\n",""))
#                #if len(tweet_str)<12: continue
#                #if not search(r'[\.a-z0-9]', tweet_str): continue
#                if search("[\t ]rt @.+", tweet_str):
#                    rt=True
#                tweet_str=tweet_str[1:]
#                #if search('http|www', tweet_str): continue #temporarily disabling this because we want to get an accurate count
#                #print tweet_str
#                #for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
#                #   if w not in words:
#                #        words |= set([w])
#                finishedQ.put([user, rt], 1)
#                #finishedQ.put(words, 1)
#            line = fh()
#        #op.close()
#        print("This file is done: %s" % self.fp)
#        self.fileHandler.close()
#        sentinelQ.put("DONE")
#        print "SentinelQ: %s, finishedQ: %s" % (sentinelQ.qsize(), finishedQ.qsize())
    
    def preprocessCorpus(self):
        global sentinelQ, finishedQ
        search = re.search
        r = string.replace
        s = string.split
        lc = string.lower
        fh = self.fileHandler.readline
        line = fh()
        print line
        while line:
        #for x in range(500000):
            if line[0]=="T":
                rt=False
                #date = s(r(r(line, "T\t", ""), "\n", ""))[0] #no need to parse line right now
                user=r(r(fh(), "U\thttp://twitter.com/",""), "\n", "")
                tweet_str = lc(r(r(fh(),"W",""),"\n",""))
                #if len(tweet_str)<12: continue
                #if not search(r'[\.a-z0-9]', tweet_str): continue
                if search("[\t ]rt @.+", tweet_str):
                    rt=True
                tweet_str=tweet_str[1:]
                #if search('http|www', tweet_str): continue #temporarily disabling this because we want to get an accurate count
                #print tweet_str
#                for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
#                    if w not in words:
#                        words |= set([w])
                finishedQ.put([user, rt], 1)
                #finishedQ.put(words, 1)
            line = fh()
        #op.close()
        print("This file is done: %s" % self.fp)
        self.fileHandler.close()
        sentinelQ.put("DONE")
        print "SentinelQ: %s, finishedQ: %s" % (sentinelQ.qsize(), finishedQ.qsize())
        
class CorpusManip:
    def __init__(self):   
        pass
    
    def run(self):
        #self.splitCorpus()
        #self.preprocessCorpus()
        #self.singleDayProcessing()
        #self.IMessedUpProcessing()
        self.convertingDaysProcessing()
        
    def IMessedUpProcessing(self):
        #I didn't put a carriage return in the final output of the words
        #thank god I have them per day lol
        finalOutput = open("/home/brian/TwitterSpring2012/RUTA/data/allWords.final", 'w')
        wordFiles = self.getAllWordFiles()
        allWords = set()
        
        r = string.replace
        
        for wordFile in wordFiles:
            perFileWords = []
            a = perFileWords.append
            wf = open(wordFile, 'r')
            rl = wf.readline
            rl()
            line = rl()
            while line:
                a(r(line, "\n",""))
                line=rl()
            allWords |= set(perFileWords)
            print "After %s, size of allWords: %s" % (wordFile, len(allWords))
        finalOutput.write("TotalWords,%s" % len(allWords))
        for word in allWords:
            finalOutput.write("%s\n" % word)
        
    def convertingDaysProcessing(self):
        global finishedQ, sentinelQ
        allfh = self.getAllFileHandlers()
        tweetProcesses=[]
        prog = SimpleProgress(214)
        x=0
        fh = [allfh[:35], allfh[35:65], allfh[65:95], allfh[95:125], allfh[125:155], allfh[155:185], allfh[185:]]
            
        for f in range(7):
            tweetProcess = TweetProcess(fh[f])
            tweetProcess.start()
            tweetProcesses.append(tweetProcess)
        prog.start()

        while not sentinelQ.full() or not finishedQ.empty():
            try:
                fileFinishedSentinel = finishedQ.get(1,5)
                x+=1
                print prog.update(x)
            except Empty:
                print "Catching empty exception, it's chill"
        print "Finito"
        
        
    def singleDayProcessing(self):
        """
        What needs to happen here:
            we need to compute the counts of words for each day
            we also need to know the number of tweets per day
            what we will be computing is the TFIDF per word per document (tweet)
            we also need to know the total number of tweets for LDA parameters
            
            What we need to get out of this:
            a pruned dictionary (unioned 1000 top tfidf terms for each day)
            number of documents per day
            
        """
        global finishedQ, sentinelQ, stopwords
        allfh = self.getAllFileHandlers()
        tweetProcesses=[]
        prog = SimpleProgress(214)
        x=0
        finalWords = set()
        fh = [allfh[:35], allfh[35:65], allfh[65:95], allfh[95:125], allfh[125:155], allfh[155:185], allfh[185:]]
            
        for f in range(7):
            tweetProcess = TweetProcess(fh[f])
            tweetProcess.start()
            tweetProcesses.append(tweetProcess)
        prog.start()

        while not sentinelQ.full() or not finishedQ.empty():
            try:
                fileFinishedSentinel = finishedQ.get(1,5)
                x+=1
                prog.update(x)
#                words = finishedQ.get(1, 5)
#                x+=1
#                finalWords |= words
#                print "---------\nFiles Seen: %s\nFinal Word Size: %s" % (x, len(finalWords))
            except Empty:
                print "Catching empty exception, it's chill"
#        finalOutput = open("/home/brian/TwitterSpring2012/RUTA/data/allWords.final", 'w')
#        finalOutput.write("Total Words,%s" % len(finalWords))
#        for word in finalWords:
#            finalOutput.write(word)
#        finalOutput.close()
        print "Finito"
        
        
    def makeDictionary(self):
        allfh = self.getAllFileHandlers()
        
        
    def splitCorpus(self):
        global finishedQ, sentinelQ
        tweetProcesses=[]
        x=0
        total = 476553560
        outputFiles = {}
        outputFilesMembership = set()
        
        prog = SimpleProgress(total)
        for f in twitterFiles:
            print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetProcess = TweetProcess(fileHandler, f)
            tweetProcess.start()
            tweetProcesses.append(tweetProcess)
            
        prog.start()
            

        while (not sentinelQ.full()) or (not finishedQ.empty()):
            x+=1
            try:
                [tweet, op] = finishedQ.get(1, 5) #assuming words is a list of unique words, no duplicates
#                if user not in userMembershipTester:
#                    userMembershipTester |= set([user])
#                    users[user] = [0, 0] #total tweets, number of RTs
#                users[user][0]+=1
#                if rt: users[user][1]+=1
#                
                if op not in outputFilesMembership:
                    outputFilesMembership |= set([op])
                    outputFiles[op] = open(op, 'w')
                outputFiles[op].write(tweet[0])
                outputFiles[op].write(tweet[1])
                outputFiles[op].write(tweet[2])
                outputFiles[op].write("\n")
                if x%50000==0:
                    print prog.update(x)
                    #print "at %s" % x
                    print "finishedQ: %s" % finishedQ.qsize()
                    print "sentinelQ: %s" % sentinelQ.qsize()
                    print "Length of outputFiles: %s" % len(outputFiles)
                    print "\n\n-----\n"
            except Empty:
                print "Catching empty exception, it's chill"
        
        for fh in outputFiles:
            outputFiles[fh].close()
                    
            
        print "Done with all threads, corpus should be split"


        print "Finito"
        
        
    """
    This method is intended to assist in developing a dictionary for the LDA process
    It will go through and count the document frequency of each word
    in addition, it wil also be counting the RT frequencyof each user and their total tweets
    Some assumptions: tweets with http, www will count towards tweet and RT in this case, because
    we are assuming the removal of bots via user restriction.  
    
    The cutoff lines for users and dictionary:
    -words with frequency: 10<f<.7*totalDocs will be removed
    -stop words will be removed
    -users with no RTs will be removed (I want to verify this metric, so tentative for now)
    --This might end up being a (noRT^hasURLs) sort of thing
    
    Eventually we will be partitioning all the tweets into their seperate days. the only reason I don't do this now is because I will be also removing
    tweets that by users that get pruned 
    """
    def preprocessCorpus(self):
        global finishedQ, sentinelQ
        tweetProcesses=[]
        x=0
        total = 476553560
        
        userMembershipTester = set()
        users = {}
        
        dictionaryMembershipTester = set()
        dictionary = {}
        
        prog = SimpleProgress(total)
        for f in twitterFiles:
            print "Starting file %s" % f        
            fileHandler = open("%s%s" % (twitterFilepath, f))
            tweetProcess = TweetProcess(fileHandler, f)
            tweetProcess.start()
            tweetProcesses.append(tweetProcess)
            
        prog.start()
            

        while (not sentinelQ.full()) or (not finishedQ.empty()):
            x+=1
            try:
                [user, rt] = finishedQ.get(1, 5) #assuming words is a list of unique words, no duplicates
                if user not in userMembershipTester:
                    userMembershipTester |= set([user])
                    users[user] = [0, 0] #total tweets, number of RTs
                users[user][0]+=1
                if rt: users[user][1]+=1
                if x%50000==0:
                    print prog.update(x)
                    #print "at %s" % x
                    print "finishedQ: %s" % finishedQ.qsize()
                    print "sentinelQ: %s\n\n-----\n" % sentinelQ.qsize()
                    print "Length of users: %s" % len(users)
            except Empty:
                print "Catching empty exception, it's chill"
                
                    
            
        print "Done with all threads, printing results to a file"
        extensions=[".predictionary", ".userstats"]
        filepath = "/home/brian/TwitterSpring2012/RUTA/data/corpus"
        
#        allfh = open("%s%s" % (filepath, extensions[0]), 'w')
#        limitedfh = open("%s%s.pruned" % (filepath, extensions[0]), 'w')
#        for word in dictionary:
#            if dictionary[word]>10 and dictionary[word]<0.7*total:
#                limitedfh.write("%s,%s\n" % (word, dictionary[word]))
#            allfh.write("%s,%s\n" % (word, dictionary[word]))
#        allfh.close()
#        limitedfh.close()
        
        allfh = open("%s%s" % (filepath, extensions[1]), 'w')
        rtonlyfh = open('%s%s.rtonly' % (filepath, extensions[1]), 'w')
        for user in users:
            if users[user][1]>0:
                rtonlyfh.write("%s,%s,%s\n" % (user, users[user][0], users[user][1]))
            allfh.write("%s,%s,%s\n" % (user, users[user][0], users[user][1]))
        allfh.close()
        rtonlyfh.close()


        print "Finito"
        
    
    def getAllFileHandlers(self):
        global fileQ
        path = "/media/OS/twitterdata"
        
        months = commands.getoutput("ls %s" % path).split("\n")[:-1]
        allfilehandlers=[]
        
        for m in months:
                days = commands.getoutput("ls %s/%s" % (path, m)).split("\n")
                for day in days:
                    if re.search("words", day) or re.search("converted", day) or re.search("stats", day):
                        continue
                    f = "%s/%s/%s" % (path, m, day)
                    print f
                    allfilehandlers.append(f)
        return allfilehandlers

    def getAllWordFiles(self):
        global fileQ
        path = "/media/OS/twitterdata"
        
        months = commands.getoutput("ls %s" % path).split("\n")[:-1]
        allfilehandlers=[]
        
        for m in months:
                days = commands.getoutput("ls %s/%s" % (path, m)).split("\n")
                for day in days:
                    if re.search("words", day):
                        f = "%s/%s/%s" % (path, m, day)
                        print f
                        allfilehandlers.append(f)
        return allfilehandlers

        
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
  

stopwords=['a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z']

  
C = CorpusManip()
C.run()






