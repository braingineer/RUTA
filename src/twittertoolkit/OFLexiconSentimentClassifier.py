"""
Description

written by brian mcmahan, 2/26/2012
"""

import GlobalConstants
from lexicontoolkit.OFSentimentLexiconParser import parseLexicon, sentiment

verbose = GlobalConstants.VERBOSE

if verbose:
    log_filename=GlobalConstants.GEN_LOG_FILENAME_WITH_TIMESTAMP("OFLexiconClassifier")
    log_file = open(log_filename, 'a')

def log(line):
    if verbose:
        GlobalConstants.LOG(log_file, line)
        
        
class OFLexiconSentimentClassifier:
    #process:
    #get lexicon
    #proceed through tweets, aggregating scores for the corresponding day
    #output results for sanity check
    def __init__(self):
        self.lexicon = parseLexicon()
        
    pass