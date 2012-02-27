baseDir = "/home/brian/TwitterSpring2012/RUTA/"

filepath="data/opinionfinder.lexicon.originalformat.tff"

from nltk import word_tokenize

def parseLexicon():
    fh = open(baseDir+filepath)
    d = dict()
    line = fh.readline()
    x=0
    while (line):
        x+=1
        [polarity, sent] = parseline(line)
        if polarity not in d:
            d[polarity] = set()
        d[polarity] |= set([sent])
        line = fh.readline()

    
    
    #print len(d)
    #for x in d:
    #    print len(d[x]), x

    return [d["positive"] | d["both"], (d["negative"] | d["weakneg"] | d["both"])]
    
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
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.lemma==other
        if other.lemma==self.lemma and other.pos==self.pos:
            return True
        return False


    
    
t = parseLexicon()
print len(t[0])
print len(t[1])