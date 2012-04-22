#imports
from multiprocessing import Queue, Process
from Queue import Empty
from operator import itemgetter
import string, re, time, math, os, cPickle
from nltk import word_tokenize, wordpunct_tokenize, regexp_tokenize
from nltk.corpus import wordnet as wn
import numpy as n
from collections import deque
global influence_model, of_lexicon, gpoms_lexicon, finished_queue, num_processes, corpus_set
num_processes = 2






class mood_object:
    def __init__(self, wordVector, recurDepth, name):   
        self.wordVector = wordVector
        self.recurDepth = recurDepth
        self.name = name


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


class SentimentProcess(Process):
    def __init__(self, file_pairs):
        Process.__init__(self)
        self.file_pairs = file_pairs
        
    def run(self):
        global finished_queue, of_lexicon, gpoms_lexicon, influence_model, corpus_set
        search = re.search
        r = string.replace
        s = string.split
        lc = string.lower
        
        for file_pair in self.file_pairs:
            tweet_file = open(file_pair[0], 'r')
            print "Got file: %s with %s gamma files" % (file_pair[0], len(file_pair[1]))
            gpom_lda=[]
            gpom_stock=[]
            gpom_rt=[]
            gpom_rt_lda=[]
            of_lda=[]
            of_stock=[0,0]
            of_rt=[0,0]
            of_rt_lda=[]
            for i in range(30):
                of_lda.append([0,0])
                of_rt_lda.append([0,0])
            for i in range(6):
                gpom_lda.append([])
                gpom_stock.append(0)
                gpom_rt.append(0)
                gpom_rt_lda.append([])
                for j in range(30):
                    gpom_lda[i].append(0)
                    gpom_rt_lda[i].append(0)
            fh = tweet_file.readline
            line = fh()
            batch = 0
            while line:
                gamma = n.loadtxt(file_pair[1][batch])
                batchD = 0
                while batchD<150000 and line:
                    if line[0]=="T":
                        user=r(r(fh(), "U\thttp://twitter.com/",""), "\n", "")
                        tweet_str = lc(r(r(fh(),"W",""),"\n",""))
                        
                        has_gamma = False
                        has_influence=False
                        
                        for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                            has_gamma+=w in corpus_set
                        if has_gamma:
                            topic = n.argmax(gamma[batchD,:]/n.sum(gamma[batchD,:]))
                            batchD+=1
                        
                        if user in influence_model[1]:
                            has_influence = True
                            influence_score = influence_model[0][user][1]
                                                  
                        for w in regexp_tokenize(tweet_str, pattern='\w+|\$[\d\.]+\S+'):
                            if w in of_lexicon[0]:
                                of_stock[0]+=1.
                                if has_gamma:
                                    of_lda[topic][0]+=1.
                                if has_influence:
                                    of_rt[0]+=influence_score
                                    if has_gamma:
                                        of_rt_lda[topic][0]+=influence_score
                            if w in of_lexicon[1]:
                                of_stock[1]+=1.
                                if has_gamma:
                                        of_lda[topic][1]+=1.
                                if has_influence:
                                    of_rt[1]+=influence_score
                                    if has_gamma:
                                        of_rt_lda[topic][1]+=influence_score
                            
                            if w in gpoms_lexicon[0]:
                                pom_tup = gpoms_lexicon[1][w]
                                gpom_stock[pom_tup[0]]+=pom_tup[1]
                                if has_gamma:
                                        gpom_lda[pom_tup[0]][topic]+=pom_tup[1]
                                if has_influence:
                                    gpom_rt[pom_tup[0]]+=pom_tup[1]*influence_score
                                    if has_gamma:
                                        gpom_rt_lda[pom_tup[0]][topic]+=pom_tup[1]*influence_score
                    line = fh()
                batch+=1
            finished_queue.put((file_pair[0],gpom_lda,gpom_stock,gpom_rt,gpom_rt_lda,of_lda,of_stock,of_rt,of_rt_lda), 1)
            #in between file pairs
            #push the results
        print "finito"

class OFLexicon:
    def __init__(self):
        pass
    
    def parseLexicon(self):
        baseDir = "/home/brian/TwitterSpring2012/RUTA/"
        filepath="data/opinionfinder.lexicon.originalformat.tff"
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
    
        return [d["strongsubj-positive"] | d["weaksubj-positive"], d["strongsubj-negative"] | d["weaksubj-negative"]]
        
    def parseline(self, line):
        x=self.todict(word_tokenize(line))
        return ["%s-%s" % (x['type'], x["priorpolarity"]), sentiment(x["word1"], x["type"], x["pos1"], x["priorpolarity"])]
        
    def todict(self, tokens):
        d=dict()
        for y in range(len(tokens)):
            if tokens[y]=="=" and y!=0 and y!=len(tokens):
                d[tokens[y-1]]=tokens[y+1]
        return d
    


class WNPOMS:
    def __init__(self):
        pass
    
    #assumes input is an array with 2 entries, each an array of words of opposite sentiment
    #these seed words are vitally important.
    #example: S=[['happy', 'ecstatic', 'elated', 'excited'], ['sad', 'morose', 'depressed']] 
    def propagate(self, S, iter):
        Sn=[]
        T=[]
        for i in range(len(S)):
            Sn.append(set())
            T.append([])
            for j in range(len(S[i])):
                #the error is stupid. it's not real. ignore it. eclipse is dumb. comment logged at 5:30 am. =)
                Sn[i] |= set(wn.synsets(S[i][j], wn.ADJ)) #@UndefinedVariable is stupid
            T[i].append(Sn[i])
    
        return self._recurprop(T, iter, 0)
        
    
    def _recurprop(self, T, m, depth):
        if m==depth:
            return T
        for j in range(len(T)):
            newSame = self.samePolarity(T[j][depth])
            otherOpposite=set()
            for k in range(len(T)):
                if k!=j:
                    otherOpposite |= self.otherPolarity(T[k][depth])
            T[j].append(newSame | otherOpposite)
        
        return self._recurprop(T, m, depth+1)
    
    def samePolarity(self, synsets):
        newsynsets=set()
        for synset in synsets:
            newsynsets |= set([synset]) | set(synset.also_sees()) | set(synset.similar_tos())
            for lemma in synset.lemmas:
                for alt_lemma in (lemma.derivationally_related_forms() + lemma.pertainyms()):
                    newsynsets |= set([alt_lemma.synset])
        return newsynsets
        
    def otherPolarity(self, synsets):
        newsynsets = set()
        for synset in synsets:
            for lemma in synset.lemmas:
                for alt_lemma in lemma.antonyms():
                    newsynsets |= set([alt_lemma.synset])
                    
        return newsynsets
                
    def moodCalc(self, mood):
        T = self.propagate(mood.wordVector, mood.recurDepth)
        pos = T[0]
        posSet={}
        x=0
        for epoch in pos:
            posSet[x]= epoch
            x+=1
        return posSet
    
    def stripParse(self, T):
        ret=[]
        information = {}
        for depth in T:
            information[depth] = []
            depthSet = T[depth]
            for syn in depthSet:
                v = string.split(string.replace(syn.name,"_", " "), ".")[0]
                if v not in ret:
                    ret.append(v)
                    information[depth].append(v)
        return information

    def makeLexicon(self):
        
        Tension= mood_object([['tense', 'shaky', 'on-edge', 'panicky', 'uneasy', 'restless', 'nervous', 'anxious'], ['relaxed']], 3, "Tension")
        Depression = mood_object([['unhappy', 'sorry-for-things-done', 'sad', 'blue', 'hopeless', 'unworthy', 'discouraged', 'lonely', 'miserable', 'gloomy', 'desperate', 'helpless', 'worthless', 'terrified', 'guilty'], []], 2, "Depression")
        Anger = mood_object([['anger', 'peeved', 'grouchy', 'spiteful', 'annoyed', 'resentful', 'bitter', 'ready-to-fight','rebellious', 'deceived', 'furious', 'bad-tempered'], []], 3, "Anger")
        Vigour = mood_object([['lively', 'active', 'energetic', 'cheerful', 'alert', 'fell of pep', 'carefree', 'vigorous'], []], 3, "Vigour")
        Fatigue = mood_object([['worn-out', 'listless', 'fatigued', 'exhausted', 'sluggish', 'weary', 'bushed'], []], 3, "Fatigue")
        Confusion = mood_object([[ 'confused', 'unable-to-concentrate', 'muddled', 'bewildered', 'forgetful', 'uncertain-about-things'], ['efficient']], 3, "Confusion")
        ProfileOfMoods = [Tension, Depression, Anger, Vigour, Fatigue, Confusion]
        
        final = {}
        x=0
        totSet = set()
        totLookup = {}
        for mood in ProfileOfMoods:
            T = self.moodCalc(mood)
            info = self.stripParse(T)
            for word in mood.wordVector[0]:
                totLookup[word]=(x, 1.)
            for depth in info:
                totSet |= set(info[depth])
                for word in info[depth]:
                    if word not in totLookup:
                        totLookup[word]=(x, 1./(1+depth))
                    else:
                        if totLookup[word][1]<(1./(1+depth)):
                            totLookup[word]=(x, 1./(1+depth))
            x+=1
        print "The WNPOMS is %s words" % len(totLookup)
        return (totSet, totLookup)


        
class SimpleProgress:
    def __init__(self, total):
        self.total = total
    
    def start(self):
        self.start = time.time()
        
    def update(self, x):
        elapsed = time.time()-self.start
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

class CompleteSentiment:

    
    def __init__(self):
        global of_lexicon, influence_model, gpoms_lexicon, finished_queue, corpus_set
        
        print "Making OFLexicon"
        of = OFLexicon()
        of_lexicon = of.parseLexicon()
        
        print "Making WordNet POMS Lexicon"
        wnpoms = WNPOMS()
        gpoms_lexicon = wnpoms.makeLexicon()
        
        print "Loading Influence Model"
        influence_model = [cPickle.load(open("/media/bigdrive/RTCounts.pkl"))]
        influence_model.append(set(influence_model[0].keys()))
        
        finished_queue = Queue(10000)
        
        corpusDictFile = open("/home/brian/TwitterSpring2012/RUTA/data/top15k.final", 'r')
        corpus_set = set()
        fl = corpusDictFile.readline
        line = fl() 
        while line:
            corpus_set.add(string.split(string.replace(line, "\n", ""), ',')[0])
            line = fl()
        corpusDictFile.close()


    def getAllFileHandlers(self):
        global fileQ
        path = "/media/OS/twitterdata"
        
        months = os.listdir("%s" % path)[:-1]
        allfilehandlers=[]
        
        for m in months:
            days = os.listdir("%s/%s" % (path, m))
            days.sort()
            poss_gammas = os.listdir("/media/bigdrive/twitteroutput/%s/" % m)
            poss_gammas.sort()
            poss_gammas = deque(poss_gammas)
            for day in days:
                if re.search("words", day) or re.search("converted", day) or re.search("stats", day):
                    continue
                f = "%s/%s/%s" % (path, m, day)
                day_gammas=[]
                while True:
                    if len(poss_gammas)==0:
                        break
                    if poss_gammas[0].split(".")[0]==day:
                        day_gammas.append("/media/bigdrive/twitteroutput/%s/%s" % (m, poss_gammas.popleft()))
                    else:
                        break
                #print f, day_gammas
                print f, len(day_gammas)
                allfilehandlers.append((f, day_gammas))
        return allfilehandlers

    def run(self):
        global finished_queue, num_processes
        all_files = self.getAllFileHandlers()
        
        root_out_dir="/media/bigdrive/timeseries/"
        gpom_lda_path="gpom_lda/"
        gpom_stock_path="gpom_stock/"
        gpom_rt_path="gpom_rt/"
        gpom_rt_lda_path="gpom_rt_lda/"
        of_stock_path="of_stock/"
        of_lda_path="of_lda/"
        of_rt_path="of_rt/"
        of_rt_lda_path="of_rt_lda/"
        dims = ['tension', 'depression', 'anger', 'vigour', 'fatigue', 'confusion']
        fh = []
        for f in range(len(all_files)):
            if len(fh)<=f%num_processes:
                fh.append([])
            fh[f%num_processes].append(all_files[f])
        
        prog = SimpleProgress(len(all_files))
        x=0        
        
        print "Variable initialization done, starting processes"
        
        processes=[]
        for i in range(num_processes):
            proc = SentimentProcess(fh[i])
            proc.start()
            processes.append(proc)
        
        prog.start()
        
        while len(processes)>0:
            try:
                
                #what is the form of the data we want back?
                #we want the seed word, it's neighbor, the number of occurences they have together
                (file_path,gpom_lda,gpom_stock,gpom_rt,gpom_rt_lda,of_lda,of_stock,of_rt,of_rt_lda) = finished_queue.get(1, 2)
                file_path = file_path.split("/")
                (day,month)=(file_path.pop(), file_path.pop())
                for i in range(6):
                    gpom_lda_out_file = open("%s%s%s.%s.%s" % (root_out_dir, gpom_lda_path, dims[i], month, day), 'w')
                    gpom_rt_lda_out_file = open("%s%s%s.%s.%s" % (root_out_dir, gpom_rt_lda_path, dims[i], month, day), 'w')
                    gpom_stock_out_file = open("%s%s%s.%s.%s" % (root_out_dir, gpom_stock_path, dims[i], month, day), 'w')
                    gpom_rt_out_file = open("%s%s%s.%s.%s" % (root_out_dir, gpom_rt_path, dims[i], month, day), 'w')
                    for j in range(30):
                        gpom_lda_out_file.write("%s\n" % gpom_lda[i][j])
                        gpom_rt_lda_out_file.write("%s\n" % gpom_rt_lda[i][j])
                    gpom_stock_out_file.write("%s\n" % gpom_stock[i])
                    gpom_rt_out_file.write("%s\n" % gpom_rt[i])
                    
                of_lda_out_file = open("%s%s%s.%s" % (root_out_dir, of_lda_path, month, day), 'w')
                of_rt_out_file = open("%s%s%s.%s" % (root_out_dir, of_rt_path, month, day), 'w')
                of_rt_lda_out_file = open("%s%s%s.%s" % (root_out_dir, of_rt_lda_path, month, day), 'w')
                of_stock_out_file = open("%s%s%s.%s" % (root_out_dir, of_stock_path, month, day), 'w')
                                    
                for i in range(30):
                    of_lda_out_file.write("%s,%s\n" % (of_lda[i][0], of_lda[i][1]))
                    of_rt_lda_out_file.write("%s,%s\n" % (of_rt_lda[i][0], of_rt_lda[i][1]))
                of_stock_out_file.write("%s,%s\n" % (of_stock[0], of_stock[1]))
                of_rt_out_file.write("%s,%s" % (of_rt[0], of_rt[1]))
                
                gpom_lda_out_file.close()
                gpom_rt_out_file.close()
                gpom_stock_out_file.close()
                gpom_rt_lda_out_file.close()
                of_lda_out_file.close()
                of_rt_out_file.close()
                of_stock_out_file.close()
                of_rt_lda_out_file.close()
                
                print "Finished with a round for %s/%s" % (month, day)
                x+=1
                print prog.update(x)
                
                for proc in processes:
                    if proc.is_alive():
                        continue
                    print "Found dead process. I hope we're at the end"
                    proc.join(1)
                    processes.remove(proc)
                
            except Empty:
                print "Waiting on processes to give me stuff.........%s" % time.ctime()
                for proc in processes:
                    if proc.is_alive():
                        continue
                    print "Found dead process. I hope we're atthe end"
                    proc.join(1)
                    processes.remove(proc)
            
        print "Ding dong the processes are dead"
        print "We should have all of our time series"
        print "Finito"
            
   

if __name__ == "__main__":
    print "Good Luck"
    main_process = CompleteSentiment()
    main_process.run()
    
