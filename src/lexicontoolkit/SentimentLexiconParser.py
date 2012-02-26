baseDir = "/home/brian/TwitterSpring2012/RUTA/"

filepath="data/opinionfinder.lexicon.originalformat.tff"

from nltk import word_tokenize

def parseLexicon():
    #testing
    fh = open(baseDir+filepath)
    d = dict()
    line = fh.readline()
    while (line):
        [polarity, sent] = parseline(line)
        #if (polarity!="positive" and polarity!="negative" and polarity!="neutral"):
        #    print line
        #    print word_tokenize(line)
        if polarity not in d:
            d[polarity] = set()
        d[polarity] |= set([sent])
        line = fh.readline()

    print len(d)
    for x in d:
        print len(d[x]), x
    
def parseline(line):
    x=todict(word_tokenize(line))
    return [x["priorpolarity"], sentiment(x["word1"], x["type"], x["pos1"], x["priorpolarity"])]
    
def todict(tokens):
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


    
    
parseLexicon()