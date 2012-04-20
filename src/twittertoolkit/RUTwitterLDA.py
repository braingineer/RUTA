#!/usr/bin/python
"""NOTE!!!"""
#  The original contents of this file come from the following source.  
#  This was only modified to allow for better integration into a twitter topic modeling project and parallelized for such

# Copyright (C) 2010  Matthew D. Hoffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public Licens e as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import cPickle, string, numpy as n, getopt, sys, random, time, re, pprint, multiprocessing, math, commands

from Queue import Empty
from scipy.special import gammaln, psi

import onlineldavb

#Global Constants
K=30
D=476553560
W=19977
alpha=1./K
eta=1./K

numProcesses=7
finishedQueue = multiprocessing.Queue()


n.random.seed(100000001)
meanchangethresh = 0.001

def dirichlet_expectation(alpha):
    """
    For a vector theta ~ Dir(alpha), computes E[log(theta)] given alpha.
    """
    if (len(alpha.shape) == 1):
        return(psi(alpha) - psi(n.sum(alpha)))
    return(psi(alpha) - psi(n.sum(alpha, 1))[:, n.newaxis])


class ExpectationProcess(multiprocessing.Process):
    def __init__(self, twitterfile, _lambda, expElogbeta):
        multiprocessing.Process.__init__(self)
        self.file = twitterfile
        self._lambda = _lambda 
        self.expElogbeta = expElogbeta




    def run(self):
        global K, D, W, alpha, meanchangethresh, finishedQueue
        
        _lambda = self._lambda
        expElogbeta = self.expElogbeta
        
        
        """
        Given a mini-batch of documents, estimates the parameters
        gamma controlling the variational distribution over the topic
        weights for each document in the mini-batch.

        Arguments:
        docs:  List of D documents. Each document must be represented
               as a string. (Word order is unimportant.) Any
               words not in the vocabulary will be ignored.

        Returns a tuple containing the estimated values of gamma,
        as well as sufficient statistics needed to update lambda.
        """
        split = string.split
        replace = string.replace
        dot = n.dot
        exp = n.exp
        mean = n.mean
        
        statsHandler = open("%s.stats" % self.file, 'r')
        batchD = eval(split(replace(statsHandler.readline(), '\n', ''), ',')[1])
        print "%s has %s docs" % (self.file, batchD)
        statsHandler.close()
        fileHandler = open("%s.converted" % self.file, 'r')
        fh = fileHandler.readline
        line = fh()
        batchRound=0
        while line:
            batchD=0
            wordids=[]
            wordcts=[]
            batchRound+=1
            while batchD<150000 and line:
                line = split(replace(line, '\n', ''), ' ')
                docIDs=[]
                docCTs=[]
                for wordUnits in line[1:]:
                    [wordid, count] = split(wordUnits, ':')
                    docIDs.append(int(wordid))
                    docCTs.append(int(count))
                wordids.append(docIDs)
                wordcts.append(docCTs)
                line = fh()
                batchD+=1
            
                
            # Initialize the variational distribution q(theta|gamma) for
            # the mini-batch
            #print "making gamma"
            gamma = 1*n.random.gamma(100., 1./100., (batchD, K))
            #print "making expectation"
            Elogtheta = dirichlet_expectation(gamma)
            #print "exponentiating expection"
            expElogtheta = n.exp(Elogtheta)
    
            sstats = n.zeros(_lambda.shape)
            # Now, for each document d update that document's gamma and phi
            it = 0
            meanchange = 0
            print "Starting the document expectation part for %s" % self.file
            for d in range(0, batchD):
                if d%20000==0:
                    print "Fitting document %s in %s" % (d, self.file)
                # These are mostly just shorthand (but might help cache locality)
                ids = wordids[d]
                cts = wordcts[d]
                gammad = gamma[d, :]
                Elogthetad = Elogtheta[d, :]
                expElogthetad = expElogtheta[d, :]
                expElogbetad = expElogbeta[:, ids]
                # The optimal phi_{dwk} is proportional to 
                # expElogthetad_k * expElogbetad_w. phinorm is the normalizer.
                phinorm = n.dot(expElogthetad, expElogbetad) + 1e-100
                # Iterate between gamma and phi until convergence
                for it in range(0, 100):
                    lastgamma = gammad
                    # We represent phi implicitly to save memory and time.
                    # Substituting the value of the optimal phi back into
                    # the update for gamma gives this update. Cf. Lee&Seung 2001.
                    gammad = alpha + expElogthetad * dot(cts / phinorm, expElogbetad.T)
                    Elogthetad = dirichlet_expectation(gammad)
                    expElogthetad = exp(Elogthetad)
                    phinorm = dot(expElogthetad, expElogbetad) + 1e-100
                    # If gamma hasn't changed much, we're done.
                    meanchange = mean(abs(gammad - lastgamma))
                    #if it%20==0: 
                    #    print "%s iteration for %s" % (it, self.file)
                    if (meanchange < meanchangethresh):
                        break
                gamma[d, :] = gammad
                # Contribution of document d to the expected sufficient
                # statistics for the M step.
                sstats[:, ids] += n.outer(expElogthetad.T, cts/phinorm)
    
            # This step finishes computing the sufficient statistics for the
            # M step, so that
            # sstats[k, w] = \sum_d n_{dw} * phi_{dwk} 
            # = \sum_d n_{dw} * exp{Elogtheta_{dk} + Elogbeta_{kw}} / phinorm_{dw}.
            sstats = sstats * expElogbeta
    
            finishedQueue.put((gamma, sstats, batchD, self.file, batchRound), 1)        
                
                
                
        fileHandler.close()
        print "Finished with %s" % self.file

        

class RUTwitterLDA:
    def __init__(self):
        pass
    
    def run(self):
        #self.topicModelTwitter()
        self.topicModelTwitter_fitTopics()
    
    def getAllFiles(self):
        global fileQ
        path = "/media/OS/twitterdata"
        
        months = commands.getoutput("ls %s" % path).split("\n")[:-1]
        allfilehandlers=[]
        
        for m in months:
                days = commands.getoutput("ls %s/%s" % (path, m)).split("\n")
                for day in days:
                    if re.search("words", day) or re.search("converted", day) or re.search("stats", day) or re.search("gamma", day) or re.search("lambda", day):
                        continue
                    f = "%s/%s/%s" % (path, m, day)
                    print f
                    allfilehandlers.append(f)
        return allfilehandlers

    def messedUpModelingTwitter(self):
        global numProcesses, finishedQueue, eta, D, K, W
        files = self.getAllJuneFiles()
        
        x=0
        prog = SimpleProgress(D-454688732)
        
        tau_0=1024
        kappa=0.7
        epoch=4643
        

    def topicModelTwitter_fitTopics(self):
        global numProcesses, finishedQueue, eta, D, K, W
        files = self.getAllFiles()
        
        x=0
        prog = SimpleProgress(D)
        
        
        tau_0=1024
        kappa=0.7
        epoch = 0
        
        _lambda = n.loadtxt('/home/brian/TwitterSpring2012/RUTA/data/final_result.lambda.dat')
        Elogbeta = dirichlet_expectation(_lambda)
        expElogbeta = n.exp(Elogbeta)
        
        eProcs = []
        for i in range(numProcesses):
            TFile = files.pop()
            eProcs.append(ExpectationProcess(TFile, _lambda, expElogbeta))
            eProcs[i].start()
            
        prog.start()
        while len(eProcs)>0:
            
                try:
                    # Do an E step to update gamma, phi | lambda for this
                    # mini-batch. This also returns the information about phi that
                    # we need to update lambda.
                    (gamma, sstats, batchsize, filename, batchRound) = finishedQueue.get(1,2)
                    print "Received gamma fit for part %s of %s," % (batchRound, filename)
                    #print "Proceeding to fit lambda to it"
                    #grab updates, update lambda, then find the dead thread and create a new one
                    
                    
                    # rhot will be between 0 and 1, and says how much to weight
                    # the information we got from this mini-batch.
                    #rhot = pow(tau_0+epoch, -kappa)
        
                    
                    # Update lambda based on documents.
                    #_lambda = _lambda*(1-rhot) + rhot*(eta+1.*D*sstats/batchsize)
                    #Elogbeta = dirichlet_expectation(_lambda)
                    #expElogbeta = n.exp(Elogbeta)
                    x+=batchsize
                    epoch+=1        
                    print prog.update(x)    
                                    
                    for proc in eProcs:
                        if proc.is_alive():
                            continue
                        proc.join(1)
                        if len(files)>0:
                            i = eProcs.index(proc)
                            eProcs[i] = ExpectationProcess(files.pop(), _lambda, expElogbeta)
                            eProcs[i].start()
                        else:
                            eProcs.remove(proc)
                    filenameSplitUp = string.split(filename, "/")
                    #n.savetxt('/media/bigdrive/twitteroutput/%s/%s.lambda.dat' % (filenameSplitUp[len(filenameSplitUp)-2],filenameSplitUp[len(filenameSplitUp)-1]), _lambda)
                    n.savetxt('/media/bigdrive/twitteroutput/%s/%s.%s.gamma.dat' % (filenameSplitUp[len(filenameSplitUp)-2],filenameSplitUp[len(filenameSplitUp)-1],batchRound), gamma)
                   
                except Empty:
                    print "Working........... %s" % time.ctime()
                    for proc in eProcs:
                        if proc.is_alive():
                            continue
                        proc.join(1)
                        if len(files)>0:
                            i = eProcs.index(proc)
                            eProcs[i] = ExpectationProcess(files.pop(), _lambda, expElogbeta)
                            eProcs[i].start()
                        else:
                            eProcs.remove(proc)
                    
        print "Finished fitting gamma to all of the files"
        #n.savetxt('/home/brian/TwitterSpring2012/RUTA/data/final_result.lambda.dat', _lambda)
        #print "final lambda saved to /home/brian/TwitterSpring2012/RUTA/data/final_result.lambda.dat"
                    

        #note, gammas are created in the processes.  they are returned, along with the sufficient stats.
        #essentially we are outsourcing the E step and performing the M here. 

    def topicModelTwitter(self):
        global numProcesses, finishedQueue, eta, D, K, W
        files = self.getAllFiles()
        
        x=0
        prog = SimpleProgress(D)
        
        
        tau_0=1024
        kappa=0.7
        epoch = 0
        
        _lambda = 1*n.random.gamma(100., 1./100., (K, W))
        Elogbeta = dirichlet_expectation(_lambda)
        expElogbeta = n.exp(Elogbeta)
        
        eProcs = []
        for i in range(numProcesses):
            TFile = files.pop()
            eProcs.append(ExpectationProcess(TFile, _lambda, expElogbeta))
            eProcs[i].start()
            
        prog.start()
        while len(eProcs)>0:
            
                try:
                    # Do an E step to update gamma, phi | lambda for this
                    # mini-batch. This also returns the information about phi that
                    # we need to update lambda.
                    (gamma, sstats, batchsize, filename, num) = finishedQueue.get(1,2)
                    print "Received data from %s" % filename
                    print "Proceeding to fit lambda to it"
                    #grab updates, update lambda, then find the dead thread and create a new one
                    
                    
                    # rhot will be between 0 and 1, and says how much to weight
                    # the information we got from this mini-batch.
                    rhot = pow(tau_0+epoch, -kappa)
        
                    
                    # Update lambda based on documents.
                    _lambda = _lambda*(1-rhot) + rhot*(eta+1.*D*sstats/batchsize)
                    Elogbeta = dirichlet_expectation(_lambda)
                    expElogbeta = n.exp(Elogbeta)
                    x+=batchsize
                    epoch+=1        
                    print prog.update(x)    
                                    
                    for proc in eProcs:
                        if proc.is_alive():
                            continue
                        proc.join(1)
                        if len(files)>0:
                            i = eProcs.index(proc)
                            eProcs[i] = ExpectationProcess(files.pop(), _lambda, expElogbeta)
                            eProcs[i].start()
                        else:
                            eProcs.remove(proc)
                    filenameSplitUp = string.split(filename, "/")
                    n.savetxt('/media/bigdrive/twitteroutput/%s/%s.lambda.dat' % (filenameSplitUp[len(filenameSplitUp)-2],filenameSplitUp[len(filenameSplitUp)-1]), _lambda)
                    #n.savetxt('/media/bigdrive/twitteroutput/%s/%s.%s.gamma.dat' % (filenameSplitUp[len(filenameSplitUp)-2],filenameSplitUp[len(filenameSplitUp)-1],epoch), gamma)
                   
                except Empty:
                    print "Working........... %s" % time.ctime()
                    for proc in eProcs:
                        if proc.is_alive():
                            continue
                        proc.join(1)
                        if len(files)>0:
                            i = eProcs.index(proc)
                            eProcs[i] = ExpectationProcess(files.pop(), _lambda, expElogbeta)
                            eProcs[i].start()
                        else:
                            eProcs.remove(proc)
                    
        print "Finished the files, printing the final lambda"
        n.savetxt('/home/brian/TwitterSpring2012/RUTA/data/final_result.lambda.dat', _lambda)
        print "final lambda saved to /home/brian/TwitterSpring2012/RUTA/data/final_result.lambda.dat"
                    

        #note, gammas are created in the processes.  they are returned, along with the sufficient stats.
        #essentially we are outsourcing the E step and performing the M here. 

        
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


def main():
    """
    The point of this file is to run the topic modeling on the twitter corpus
    The files are in day-split files
    There is a parallized process which will proceed as follows:
        Each process will be passed in a copy of the variables, including the updated versions
        The lambda, and all other init variables will then be held here.  
        1.  Initially, 7 processes will be created with the blank variales and handed 1 file
        2.  The main process then sits around and waits until a process finishes
        3.  Upon finishing, the main process updates the lambda and starts a new process, passing in a new file
        4.  This repeats until all files are gone
    """
    topicModeler = RUTwitterLDA()
    topicModeler.run()
    

if __name__ == '__main__':
    main() 
