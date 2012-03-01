"""
Description

written by brian mcmahan, 2/26/2012

Deprecated 2/27/2012 for the MT sentiment classification system

"""
from nltk import word_tokenize
import time
from lexicontoolkit.OFSentimentLexiconParser import parseLexicon, sentiment

twitterFiles = ["tweets2009-06.txt","tweets2009-07.txt","tweets2009-08.txt","tweets2009-09.txt","tweets2009-10.txt","tweets2009-11.txt","tweets2009-12.txt"]
twitterFilepath = "/media/Media/tweets/bigdata/"


            
            
class logger:
    def __init__(self):
        self.BASE_DIR = "/home/brian/TwitterSpring2012/RUTA/logs/"
        self.verbose = True
        self.log_file = None
    
    def createlog(self, stub):
        if self.verbose:
            self.closelog()
            t=time.localtime()
            timestamp = "%s-%s-%s_%s.%s" % (t.tm_mon, t.tm_mday, t.tm_mday, t.tm_hour, t.tm_min)
            log_filename="%sOFLexiconClassifier.%s.%s" % (self.BASE_DIR, stub, timestamp)
            self.log_file = open(log_filename, 'a')
    
    def log(self, line):
        if self.verbose:
            self.log_file.write(line+"\n")
            
    def closelog(self):
        if self.verbose:
            if self.log_file:
                self.log_file.close()
        
class OFLexiconSentimentClassifier:
    #process:
    #get lexicon
    #proceed through tweets, aggregating scores for the corresponding day
    #output results for sanity check
    def __init__(self):
        self.POS = "positive"
        self.NEG = "negative"
        l = parseLexicon()
        self.lexicon = {self.POS:l[0], self.NEG:l[1]}
        self.dayCounts = {}
        self.debug = logger()

        
    def run(self):
        #for f in twitterFiles:
        for f in twitterFiles:
            self.debug.createlog(f)
            fileHandler = open("%s%s" % (twitterFilepath, f))
            line = fileHandler.readline()
            print "about to start"
            while line: 
                if self.isTweet(line):
                    t = self.parseTweet(line, fileHandler)
                    self.classify(self.POS,t)
                    self.classify(self.NEG,t)
                line = fileHandler.readline()
        print "done"
        for day in self.dayCounts:
            print day, self.dayCounts[day]
        self.debug.closelog()
        
    def isTweet(self, line):
        return line[0]=="T"
    
    def classify(self, polarity, item):
        #t = "\nClassifying %s to polarity %s" % (item.tweet_str, polarity)
        #b = False
        for w in word_tokenize(item.tweet_str):
            if w in self.lexicon[polarity]:
                day = (item.date.split(" "))[0]
                if day not in self.dayCounts:
                    self.dayCounts[day] = {self.POS:0, self.NEG:0}
                self.dayCounts[day][polarity]+=1
                #b = True
                #t+="\n%s classified to %s" % (w, polarity)
        #if b:
            #self.debug.log(t)

    def parseTweet(self, line, fileHandler):
            date = line
            user = fileHandler.readline()
            tweet_str = fileHandler.readline()
            return tweet(date, user, tweet_str)

class tweet:
    def __init__(self, date, user, tweet_str):
        self.date = date.replace("T\t", "").replace("\n", "")
        self.user = user.replace("U\t","").replace("\n","")
        self.tweet_str = tweet_str.replace("W\t","").replace("\n","")
        
    def __str__(self):
        return "%s\n%s\n%s" % (self.date, self.user, self.tweet_str)
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash(self.__str__())
    
    
of = OFLexiconSentimentClassifier()
of.run()