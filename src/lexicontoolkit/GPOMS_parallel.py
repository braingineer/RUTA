#!/usr/bin/python

#imports
from multiprocessing import Queue, Process
from Queue import Empty
from operator import itemgetter
import string, re, time, math, os, cPickle


#global variables

#poms
tension=['tense', 'shaky', 'on-edge', 'panicky', 'uneasy', 'restless', 'nervous', 'anxious', 'relaxed']
depression=['unhappy', 'sorry-for-things-done', 'sad', 'blue', 'hopeless', 'unworthy', 'discouraged', 'lonely', 'miserable', 'gloomy','desperate', 'helpless', 'worthless', 'terrified', 'guilty']
anger=['anger', 'peeved', 'grouchy', 'spiteful', 'annoyed', 'resentful','bitter', 'ready-to-fight','rebellious', 'deceived', 'furious','bad-tempered']
vigour=['lively', 'active', 'energetic', 'cheerful', 'alert','full of pep', 'carefree', 'vigorous']
fatigue=['worn-out', 'listless', 'fatigued', 'exhausted', 'sluggish','weary', 'bushed']
confusion=['confused', 'unable-to-concentrate', 'muddled', 'bewildered','forgetful', 'uncertain-about-things', 'efficient']
poms=tension+depression+anger+vigour+fatigue+confusion

#filepaths
four_gram_filepath = "/media/OS/googledata/4gms/"
five_gram_filepath = "/media/OS/googledata/5gms/"
output_filepath="/media/bigdrive/gpoms/"
unigram_filepath="/media/OS/googledata/1gms/vocab"
#parameters
num_processors=7


#functional globals
finished_queue = Queue(10000)



class GPOMS_process(Process):
    def __init__(self, g_file, seeds=None):
        Process.__init__(self)
        self.g_file = g_file
        self.seeds = seeds
        
    def run(self):
        #self.neighbors_from_seeds()
        self.total_freq_count()
    
    def test(self, x):
        return float(string.split(x)[-1])
        
    def total_freq_count(self):
        global finished_queue
        
        fh = open(self.g_file, 'r')
        print "Loading %s" % self.g_file
        
        s = string.split
        total = 0
        for line in fh:
            total+=int(s(line)[-1])
        finished_queue.put(total,1)
        fh.close()
        print "Process has processed %s" % self.g_file
        
    def neighbors_from_seeds(self):
        global finished_queue
        
        fh = open(self.g_file, 'r')
        print "Loading %s" % self.g_file
        readline = fh.readline
        
        membership = set(self.seeds)
        
        word_memberships = {}
        output_counts = {}
        word_counts = [dict(), set()]
        for seed in membership:
            output_counts[seed] = {}
            word_memberships[seed] = set()
            
        
        s = string.split
        lc = string.lower
        search = re.search
        
        line = readline()
        total = 0
        while line:
            line = s(lc(line))
            freq = float(line[-1])
            total+=freq
            for word in line[:-1]:    
                if (not (search("[^a-z]", word))):
                    if word not in word_counts[1]:
                        word_counts[1] |= set([word])
                        word_counts[0][word]=0
                    word_counts[0][word]+=freq
                    if word in membership:
                        #add all words to dict with the freq
                        for neighbor in line[:-1]:
                            if neighbor==word or search("[^a-z]", word):
                                continue
                            if neighbor not in word_memberships[word]:
                                word_memberships[word] |= set([neighbor])
                                output_counts[word][neighbor] = 0
                            output_counts[word][neighbor]+=freq
                        
            line = readline()
        finished_queue.put((output_counts, word_counts[0] , total),1)
        print "Process has processed %s" % self.g_file
    
class GPOMS_parallel:
    def __init__(self):
        pass
    
    def run(self, seeds):
        #self.findNeighborhood(seeds)
        #self.get_total_occ()
        self.re_run_from_pickles()
    
    def getFiles(self, file_path_array):
        all_filenames=[]
        for path in file_path_array:
            files = os.listdir(path)
            for f in files:
                all_filenames.append("%s%s" % (path, f))
        return all_filenames
    
    def get_total_occ(self):
        files = self.getFiles([four_gram_filepath, five_gram_filepath])
        
        prog = SimpleProgress(len(files))
        x=0        
        
        total_occ = 0
        
        
        print "Variable initialization done, starting processes"
        
        processes=[]
        for i in range(num_processors):
            proc = GPOMS_process(files.pop())
            proc.start()
            processes.append(proc)
            
        prog.start()
    
        while len(processes)>0:
            try:
                total_occ+=finished_queue.get(1, 2)
                print "Processes alive: %s" % len(processes)
                x+=1
                print prog.update(x)
                
                for proc in processes:
                    if proc.is_alive():
                        continue
                    proc.join(1)
                    print "Found a dead process =)"
                    if len(files)>0:
                        i = processes.index(proc)
                        processes[i] = GPOMS_process(files.pop())
                        processes[i].start()
                    else:
                        print "Removing a process forevvverrr"
                        processes.remove(proc)
            except Empty:
                print "waiting...... %s" % time.ctime()
                for proc in processes:
                    if proc.is_alive():
                        continue
                    proc.join(1)
                    print "Found a dead process =)"
                    if len(files)>0:
                        i = processes.index(proc)
                        processes[i] = GPOMS_process(files.pop())
                        processes[i].start()
                    else:
                        print "Removing a process forevvverrr"
                        processes.remove(proc)
        print total_occ
        print "finito"
    
    def re_run_from_pickles(self):
        f_c = open("%sfinal_counts.dump" % output_filepath, 'r')
        w_c= open("%sword_counts.dump" % output_filepath, 'r')
        final_counts = cPickle.load(f_c)
        word_counts = cPickle.load(w_c)
        f_c.close()
        w_c.close()
        #unigram_counts = self.get_unigram_counts(final_counts)
        #update the counts with PMI
        
        total_occ = 861912214032
        
        t_stat = {}
        conditional_test = {}
        pmi = {}
        
        print "Doing tests"
        for seed in final_counts:
            t_stat[seed] = {}
            conditional_test[seed] = {}
            pmi[seed] = {}
            for neighbor in final_counts[seed][0]: #vector of words with frequencies
                if re.search("[^a-z]", neighbor):
                    continue
                freq = 1.*final_counts[seed][0][neighbor]
                mutual_prob = 1.*freq/total_occ
                seed_prob = 1.*word_counts[0][seed]/total_occ
                neighbor_prob = 1.*word_counts[0][neighbor]/total_occ
                ttest = ( mutual_prob-seed_prob*neighbor_prob ) / (math.sqrt(seed_prob*neighbor_prob))
                pmi_val = math.log(mutual_prob / (seed_prob*neighbor_prob), 2)
                conditional = mutual_prob / seed_prob
                t_stat[seed][neighbor]= ttest
                conditional_test[seed][neighbor] = conditional
                pmi[seed][neighbor] = pmi_val
                #final_counts[seed][0][neighbor] = math.log(freq/(1.*unigram_counts[seed]*unigram_counts[neighbor]), 2)
        
        #output
        print "Tests done, beginning output"
        for seed in final_counts:
            pmi_out="%spmi/%s.neighborhood" % (output_filepath, seed)
            t_test_out="%sttest/%s.neighborhood" % (output_filepath, seed)
            cond_out="%sconditional/%s.neighborhood" % (output_filepath, seed)
            
            print "Outputting %s" % seed 
            pmi_out_file = open(pmi_out, 'w')
            t_test_out_file = open(t_test_out, 'w')
            cond_out_file = open(cond_out, 'w')
            
            pmi_ordered = sorted(pmi[seed].iteritems(), key=itemgetter(1), reverse=True)
            t_test_ordered = sorted(t_stat[seed].iteritems(), key=itemgetter(1), reverse=True)
            cond_ordered = sorted(conditional_test[seed].iteritems(), key=itemgetter(1), reverse=True)
            
            for neighbor in pmi_ordered:
                pmi_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            pmi_out_file.close()
            
            for neighbor in t_test_ordered:
                t_test_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            t_test_out_file.close()
            
            for neighbor in cond_ordered:
                cond_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            cond_out_file.close()
            
            
        print "Finito"
        
    def findNeighborhood(self, seeds):
        global finished_queue, num_processors, four_gram_filepath, five_gram_filepath, output_filepath
        

        
        files = self.getFiles([four_gram_filepath, five_gram_filepath])
        
        prog = SimpleProgress(len(files))
        x=0        
        
        total_occ = 0
        word_counts = [dict(), set()]
        
        final_counts={}
        for seed in seeds:
            final_counts[seed]=[dict(), set()]
        
        print "Variable initialization done, starting processes"
        
        processes=[]
        for i in range(num_processors):
            proc = GPOMS_process(files.pop(), seeds)
            proc.start()
            processes.append(proc)
        
        prog.start()
        
        while len(processes)>0:
            try:
                #what is the form of the data we want back?
                #we want the seed word, it's neighbor, the number of occurences they have together
                (neighbors, counts, loc_total) = finished_queue.get(1, 2)
                total_occ+=loc_total
                for word in counts:
                    if word not in word_counts[1]:
                        word_counts[1] |= set([word])
                        word_counts[0][word]=0
                    word_counts[0][word]+=counts[word]
                
                print "Got a file from a process"
                for seed in seeds: #for all of the seed words
                    for neighbor in neighbors[seed]: #neighbors is a bin-type containing a list of 2-tuples for each seed word
                        if neighbor not in final_counts[seed][1]: #check for membership in set
                            final_counts[seed][1] |= set([neighbor]) #initialize membership in set
                            final_counts[seed][0][neighbor] = 0 #initialize the dict val
                        final_counts[seed][0][neighbor]+=neighbors[seed][neighbor] #increment the dict val
                print "Finished assimilating its information"
                x+=1
                print prog.update(x)
                
                for proc in processes:
                    if proc.is_alive():
                        continue
                    proc.join(1)
                    if len(files)>0:
                        i = processes.index(proc)
                        processes[i] = GPOMS_process(files.pop(), seeds)
                        processes[i].start()
                    else:
                        processes.remove(proc)
                        
                        
            except Empty:
                print "Processes are hard at work.... %s" % time.ctime()
                for proc in processes:
                    if proc.is_alive():
                        continue
                    proc.join(1)
                    if len(files)>0:
                        i = processes.index(proc)
                        processes[i] = GPOMS_process(files.pop(), seeds)
                        processes[i].start()
                    else:
                        processes.remove(proc)
        
        print "All files finished, getting unigram counts"
        f_c = open("%sfinal_counts.dump" % output_filepath, 'w')
        w_c= open("%sword_counts.dump" % output_filepath, 'w')
        cPickle.dump(final_counts, f_c)
        cPickle.dump(word_counts, w_c)
        f_c.close()
        w_c.close()
	 #unigram_counts = self.get_unigram_counts(final_counts)
        #update the counts with PMI
        
        t_stat = {}
        conditional_test = {}
        pmi = {}
        
        print "Unigram counts done, computing PMI"
        for seed in final_counts:
            t_stat[seed] = {}
            conditional_test[seed] = {}
            pmi[seed] = {}
            for neighbor in final_counts[seed][0]: #vector of words with frequencies
                freq = 1.*final_counts[seed][0][neighbor]
                mutual_prob = 1.*freq/total_occ
                seed_prob = 1.*word_counts[0][seed]/total_occ
                neighbor_prob = 1.*word_counts[0][neighbor]/total_occ
                ttest = ( mutual_prob-seed_prob*neighbor_prob ) / (math.sqrt(seed_prob*neighbor_prob))
                pmi_val = math.log(mutual_prob / (seed_prob*neighbor_prob), 2)
                conditional = mutual_prob / seed_prob
                t_stat[seed][neighbor]= ttest
                conditional_test[seed][neighbor] = conditional
                pmi[seed][neighbor] = pmi_val
                #final_counts[seed][0][neighbor] = math.log(freq/(1.*unigram_counts[seed]*unigram_counts[neighbor]), 2)
        
        #output
        print "Tests done, beginning output"
        for seed in final_counts:
            pmi_out="%spmi/%s.neighborhood" % (output_filepath, seed)
            t_test_out="%sttest/%s.neighborhood" % (output_filepath, seed)
            cond_out="%sconditional/%s.neighborhood" % (output_filepath, seed)
            
            print "Outputting %s" % seed 
            pmi_out_file = open(pmi_out, 'w')
            t_test_out_file = open(t_test_out, 'w')
            cond_out_file = open(cond_out, 'w')
            
            pmi_ordered = sorted(pmi[seed].iteritems(), key=itemgetter(1), reverse=True)
            t_test_ordered = sorted(t_stat[seed].iteritems(), key=itemgetter(1), reverse=True)
            cond_ordered = sorted(conditional_test[seed].iteritems(), key=itemgetter(1), reverse=True)
            
            for neighbor in pmi_ordered:
                pmi_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            pmi_out_file.close()
            
            for neighbor in t_test_ordered:
                t_test_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            t_test_out_file.close()
            
            for neighbor in cond_ordered:
                cond_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            cond_out_file.close()
            
            
        print "Finito"

    def get_unigram_counts(self, final_counts):
        global unigram_filepath
        
        prog = SimpleProgress(1024908267229)
        
        output_dict = dict()
        
        s = string.split
        lc = string.lower
        seeds = final_counts.keys()
        
        all_tokens = set(seeds)
        for seed in seeds:
            all_tokens |= set(final_counts[seed][0].keys())
            
        prog.start()
        unigram_file = open(unigram_filepath, 'r')
        readalot = unigram_file.readlines
        lines = readalot(1000000)
        while lines:
            for line in lines:
                line = s(lc(line))
                if line[0] in all_tokens:
                    output_dict[line[0]] = float(line[1])
            print prog.updateCuum(len(lines))
            lines = readalot(1000000)
        return output_dict
    
        

class SimpleProgress:
    def __init__(self, total):
        self.total = total
        self.runningT = 0
    
    def start(self):
        self.startTime = time.time()
        
    def update(self, x):
        elapsed = time.time()-self.startTime
        percDone = x*100.0/self.total
        estimatedTimeInSec=(elapsed*1.0/x)*self.total
        return "%s %s percent\n%s Processed\nElapsed time: %s\nEstimated time: %s\n--------" % (self.bar(percDone), round(percDone, 2), x, self.form(elapsed), self.form(estimatedTimeInSec))
    
    def updateCuum(self, x):
        self.runningT+=x
        elapsed = time.time()-self.startTime
        percDone = self.runningT*100.0/self.total
        estimatedTimeInSec=(elapsed*1.0/self.runningT)*self.total
        return "%s %s percent\n%s Processed\nElapsed time: %s\nEstimated time: %s\n--------" % (self.bar(percDone), round(percDone, 2), self.runningT, self.form(elapsed), self.form(estimatedTimeInSec))
        
        
    def form(self, t):
        hour = int(t/(60.0*60.0))
        minute = int(t/60.0 - hour*60)
        sec = int(t-minute*60-hour*3600)
        return "%s Hours, %s Minutes, %s Seconds" % (hour, minute, sec)
        
    def bar(self, perc):
        done = int(round(30*(perc/100.0)))
        left = 30-done
        return "[%s%s]" % ('|'*done, ':'*left)





if __name__ == "__main__":
    global poms
    gpom_processor = GPOMS_parallel()
    gpom_processor.run(poms)
