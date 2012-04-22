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

stopwords=set(['a', 'am', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z'])


#filepaths
four_gram_filepath = "/media/OS/googledata/4gms/"
five_gram_filepath = "/media/OS/googledata/5gms/"
output_filepath="/media/bigdrive/gpoms/"
unigram_filepath="/media/OS/googledata/1gms/vocab"
#parameters
num_processors=6


#functional globals
finished_queue = Queue(10000)



class GPOMS_process(Process):
    def __init__(self, g_file, seeds=None, g_files=None):
        Process.__init__(self)
        self.g_file = g_file
        self.seeds = seeds
        self.g_files = g_files
        
    def run(self):
        self.neighbors_from_seeds()
        #self.total_freq_count()
    
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
        global finished_queue, stopwords
        s = string.split
        lc = string.lower
        search = re.search
        for g_file in self.g_files:
            
            fh = open(g_file, 'r')
            print "Loading %s" % g_file
            readline = fh.readline
            
            membership = set(self.seeds)
            
            word_memberships = {}
            output_counts = {}
            for seed in membership:
                output_counts[seed] = {}
                word_memberships[seed] = set()

            line = readline()
            while line:
                line = s(lc(line))
                freq = float(line[-1])
                line = line[:-1]
                for word in line:    
                    if not search(".*[^a-z].*", word) and word in membership and word not in stopwords:
                        for neighbor in line:
                            if neighbor==word or search(".*[^a-z].*", word):
                                continue
                            if neighbor not in word_memberships[word]:
                                word_memberships[word] |= set([neighbor])
                                output_counts[word][neighbor] = 0
                            output_counts[word][neighbor]+=freq
                            
                line = readline()
            #finished_queue.put((output_counts, word_counts[0] , total),1)
            finished_queue.put(output_counts,1)
            print "Process has processed %s" % self.g_file
        
        
    def neighbors_from_seeds_with_wordcounts(self):
        global finished_queue
        
        fh = open(self.g_file, 'r')
        print "Loading %s" % self.g_file
        readline = fh.readline
        
        membership = set(self.seeds)
        
        word_memberships = {}
        output_counts = {}
        #word_counts = [dict(), set()]
        for seed in membership:
            output_counts[seed] = {}
            word_memberships[seed] = set()
            
        
        s = string.split
        lc = string.lower
        search = re.search
        
        line = readline()
        while line:
            line = s(lc(line))
            freq = float(line[-1])
            for word in line[:-1]:    
                if (not (search(".*[^a-z].*", word))):
                    #if word not in word_counts[1]:  #Ignoring the word counts. I have a pickle for it (; hahah
                    #    word_counts[1] |= set([word])
                    #    word_counts[0][word]=0
                    #word_counts[0][word]+=freq
                    if word in membership:
                        #add all words to dict with the freq
                        for neighbor in line[:-1]:
                            if neighbor==word or search(".*[^a-z].*", word): #why is shit sneaking past this?! FIXED
                                continue
                            if neighbor not in word_memberships[word]:
                                word_memberships[word] |= set([neighbor])
                                output_counts[word][neighbor] = 0
                            output_counts[word][neighbor]+=freq
                        
            line = readline()
        #finished_queue.put((output_counts, word_counts[0] , total),1)
        finished_queue.put(output_counts,1)
        print "Process has processed %s" % self.g_file
    
class GPOMS_parallel:
    def __init__(self):
        pass
    
    def run(self, seeds):
        #self.findNeighborhood(seeds)
        #self.get_total_occ()
        #self.re_run_from_pickles()
        self.second_order()
    
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

        #unigram_counts = self.get_unigram_counts(final_counts)
        #update the counts with PMI
        
        t_stat = {}
        conditional_test = {}
        #pmi = {}
        
        print "computing tests"
        for seed in final_counts:
            t_stat[seed] = {}
            conditional_test[seed] = {}
            #pmi[seed] = {}
            for neighbor in final_counts[seed][0]: #vector of words with frequencies
                if re.search(".*[^a-z].*", neighbor):
                    continue
                freq = 1.*final_counts[seed][0][neighbor]
                mutual_prob = 1.*freq/total_occ
                seed_prob = 1.*word_counts[0][seed]/total_occ
                neighbor_prob = 1.*word_counts[0][neighbor]/total_occ
                ttest = ( mutual_prob-seed_prob*neighbor_prob ) / (math.sqrt(seed_prob*neighbor_prob))
                #pmi_val = math.log(mutual_propmi/b / (seed_prob*neighbor_prob), 2)
                conditional = mutual_prob / seed_prob
                t_stat[seed][neighbor]= ttest
                conditional_test[seed][neighbor] = conditional
                #pmi[seed][neighbor] = pmi_val
                #final_counts[seed][0][neighbor] = math.log(freq/(1.*unigram_counts[seed]*unigram_counts[neighbor]), 2)
        
        #output
        
        
        
        print "Tests done, beginning output"
        outdir = "%s%s" % (output_filepath, "second_order/") 
        ttestdir = outdir+"ttest/"
        conddir = outdir+"conditional/"
        if not os.path.exists(ttestdir):
            os.makedirs(ttestdir)
        if not os.path.exists(conddir):
            os.makedirs(conddir)
        for seed in final_counts:
            t_test_out="%sttest/%s.neighborhood" % (outdir, seed)
            cond_out="%sconditional/%s.neighborhood" % (outdir, seed)
            
            print "Outputting %s" % seed 
            t_test_out_file = open(t_test_out, 'w')
            cond_out_file = open(cond_out, 'w')
            
            t_test_ordered = sorted(t_stat[seed].iteritems(), key=itemgetter(1), reverse=True)
            cond_ordered = sorted(conditional_test[seed].iteritems(), key=itemgetter(1), reverse=True)

            
            for neighbor in t_test_ordered:
                t_test_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            t_test_out_file.close()
            
            for neighbor in cond_ordered:
                cond_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            cond_out_file.close()
            
        #w_c.close()    
        print "Finito"


    def second_order(self):
        global stopwords
        stop = stopwords
        
        s = string.split
        r = string.replace
        
        cond_location = output_filepath+"conditional/"
        files = os.listdir(cond_location)
        
        seed_files = []
        
        for f in files:
            seed_files.append("%s%s" % (cond_location, f))
            
        seeds = []
        seed_logger = {}
        for s_f in seed_files:
            c_seeds=[]
            seed_file = open(s_f, 'r')
            line = seed_file.readline()
            seed_name = string.split(s_f, '/')[-1]
            seed_logger[seed_name] = []
            while line and len(c_seeds)<20:
                line = s(r(line, '\n', ''), ',')
                if line[1] not in stop:
                    c_seeds.append(line[1])
                    seed_logger[seed_name].append(line[1])
                line = seed_file.readline()
            seeds+=c_seeds
        #print seeds, len(seeds), len(seed_files)
        for seed in seed_logger:
            print "Seed: %s \n" % seed
            print "%s\n\n\n" % seed_logger[seed] 
        #self.general_neighboorhood_find(seeds[:len(seeds)/2], "second_order_ttest/part_one/")
        #self.general_neighboorhood_find(seeds[len(seeds)/2:], "second_order_ttest/part_two/")
        #self.make_top_files(seed_logger)
            

    def make_top_files(self, words):
        indir = ["/media/bigdrive/gpoms/second_order_ttest/part_one/ttest/", "/media/bigdrive/gpoms/second_order_ttest/part_two/ttest/"]
        file_handler_dict = {}
        for ind in indir:
            files = os.listdir(ind)
            for f in files:
                file_handler_dict[f.split('.')[0]] = "%s%s" % (ind, f)
        
        word_scores = {}
        for seed in words:
            print "Starting %s" % seed
            word_scores[seed] = {}
            for second_seed in words[seed]:
                fh = open(file_handler_dict[second_seed], 'r')
                lines = fh.readlines(200)
                for line in lines:
                    line= string.replace(line, '\n', '').split(',')
                    if line[1] not in word_scores[seed]:
                        word_scores[seed][line[1]]=0
                    word_scores[seed][line[1]]+=float(line[2])
                fh.close()
            final_scores = sorted(word_scores[seed].iteritems(), key=itemgetter(1), reverse=True)
            print "Writing to the file"
            out_h = open('/media/bigdrive/gpoms/%s.final_scores' % seed, 'w')
            for word in final_scores:
                out_h.write("%s,%s\n" % word)
            out_h.close()
        print "finito"
            
                    
                
    def general_neighboorhood_find(self, seeds, odir):
        global finished_queue, num_processors, four_gram_filepath, five_gram_filepath, output_filepath
        outdir = "%s%s" % (output_filepath, odir) 
        ttestdir = outdir+"ttest/"
        conddir = outdir+"conditional/"
        if not os.path.exists(ttestdir):
            os.makedirs(ttestdir)
        if not os.path.exists(conddir):
            os.makedirs(conddir)
        
        print "Initializing variables, we have %s seeds" % len(seeds)
        
        
        
        files = self.getFiles([four_gram_filepath, five_gram_filepath])
        
        fh = []
        for f in range(len(files)):
            if len(fh)<=f%num_processors:
                fh.append([])
            fh[f%num_processors].append(files[f])
        
        prog = SimpleProgress(len(files))
        x=0        
        
        total_occ = 861912214032
        
        final_counts={}
        for seed in seeds:
            final_counts[seed]=[dict(), set()]
        
        print "Variable initialization done, starting processes"
        
        processes=[]
        for i in range(num_processors):
            proc = GPOMS_process(None, seeds, g_files=fh[i])
            proc.start()
            processes.append(proc)
        
        prog.start()
        
        while len(processes)>0:
            try:
                #what is the form of the data we want back?
                #we want the seed word, it's neighbor, the number of occurences they have together
                neighbors = finished_queue.get(1, 2)

                contribution=0
                totsize=0
                print "Got a file from a process"
                for seed in seeds: #for all of the seed words
                    for neighbor in neighbors[seed]: #neighbors is a bin-type containing a list of 2-tuples for each seed word
                        contribution+=1
                        if neighbor not in final_counts[seed][1]: #check for membership in set
                            final_counts[seed][1] |= set([neighbor]) #initialize membership in set
                            final_counts[seed][0][neighbor] = 0 #initialize the dict val
                        final_counts[seed][0][neighbor]+=neighbors[seed][neighbor] #increment the dict val
                    totsize+=len(final_counts[seed][1])
                print "Finished assimilating its information"
                x+=1
                print prog.update(x)
                print "totsize=%s, contribution=%s" % (totsize, contribution)
                for proc in processes:
                    if proc.is_alive():
                        continue
                    print "Found dead process. I hope we're atthe end"
                    proc.join(1)
                    processes.remove(proc)
                
                        
                        
            except Empty:
                print "Processes are hard at work.... %s" % time.ctime()
                for proc in processes:
                    if proc.is_alive():
                        continue
                    print "Found dead process. I hope we're atthe end"
                    proc.join(1)
                    processes.remove(proc)
        
        print "All files finished"
        f_c = open("%sfinal_counts.dump" % outdir, 'w')
        cPickle.dump(final_counts, f_c)
        f_c.close()
        
        w_c= open("%sword_counts.dump" % output_filepath, 'r')
        word_counts = cPickle.load(w_c)
        w_c.close()
        #unigram_counts = self.get_unigram_counts(final_counts)
        #update the counts with PMI
        
        t_stat = {}
        conditional_test = {}
        #pmi = {}
        
        print "computing tests"
        for seed in final_counts:
            t_stat[seed] = {}
            conditional_test[seed] = {}
            #pmi[seed] = {}
            for neighbor in final_counts[seed][0]: #vector of words with frequencies
                if re.search(".*[^a-z].*", neighbor):
                    continue
                freq = 1.*final_counts[seed][0][neighbor]
                mutual_prob = 1.*freq/total_occ
                seed_prob = 1.*word_counts[0][seed]/total_occ
                neighbor_prob = 1.*word_counts[0][neighbor]/total_occ
                ttest = ( mutual_prob-seed_prob*neighbor_prob ) / (math.sqrt(seed_prob*neighbor_prob))
                #pmi_val = math.log(mutual_prob / (seed_prob*neighbor_prob), 2)
                conditional = mutual_prob / seed_prob
                t_stat[seed][neighbor]= ttest
                conditional_test[seed][neighbor] = conditional
                #pmi[seed][neighbor] = pmi_val
                #final_counts[seed][0][neighbor] = math.log(freq/(1.*unigram_counts[seed]*unigram_counts[neighbor]), 2)
        
        #output
        
        
        
        print "Tests done, beginning output"
        
        
            
        for seed in final_counts:
            t_test_out="%s%s.neighborhood" % (ttestdir, seed)
            cond_out="%s%s.neighborhood" % (conddir, seed)
            
            print "Outputting %s" % seed 
            t_test_out_file = open(t_test_out, 'w')
            cond_out_file = open(cond_out, 'w')
            
            t_test_ordered = sorted(t_stat[seed].iteritems(), key=itemgetter(1), reverse=True)
            cond_ordered = sorted(conditional_test[seed].iteritems(), key=itemgetter(1), reverse=True)

            
            for neighbor in t_test_ordered:
                t_test_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            t_test_out_file.close()
            
            for neighbor in cond_ordered:
                cond_out_file.write("%s,%s,%s\n" % (seed, neighbor[0], neighbor[1]))
            cond_out_file.close()
            
        w_c.close()    
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
