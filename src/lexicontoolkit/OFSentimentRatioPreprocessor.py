"""
author: gaurav kharkwal
date  : 20120309
about : Helper script to make data easier to import to Matlab.
        Removes '-' from the dates, replaces commas with tabs, and while
        so doing, computes the sentiment ratio (numPos/numNeg).

        Matlab will do the smoothing.
"""

def cleanAndWrite(ifile, ofile, posCol=1, negCol=2):
    """
    * helper function.
    * gets input and output file paths
    * opens and reads input, parses line, cleans data, computes...
        ... sentiment ratio, and outputs it to the output file. easy peasy.
    """

    ifh     = open(ifile)
    ilines  = ifh.readlines()
    ifh.close()

    olines = []
    for il in ilines:
        toks    = il.split(',')
        toks[0] = toks[0].replace('-','') # remove '-' from dates
        toks[len(toks)-1] = toks[len(toks)-1].strip()         # remove '\n' from last token

        # compute sentiment ratio
        toks.append(str(float(toks[posCol])/(float(toks[negCol]) + .1))) # .1 added for 0s

        olines.append('\t'.join(toks) + '\n')

    ofh = open(ofile, 'w')
    for ol in olines:
        ofh.write(ol)
    ofh.close()


if __name__ == "__main__":
    ifile = "../../data/OFLexicon.results.cast.notweighted.nonetural"
    ofile = "../../data/OFL.C.NW.NN.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.cast.notweighted.withneutral"
    ofile = "../../data/OFL.C.NW.N.txt"

    cleanAndWrite(ifile,ofile,2,1)

    ifile = "../../data/OFLexicon.results.cast.weighted.noneutral"
    ofile = "../../data/OFL.C.W.NN.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.cast.weighted.withneutral"
    ofile = "../../data/OFL.C.W.N.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.notcast.notweighted.nonetural"
    ofile = "../../data/OFL.NC.NW.NN.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.notcast.notweighted.withneutral"
    ofile = "../../data/OFL.NC.NW.N.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.notcast.weighted.noneutral"
    ofile = "../../data/OFL.NC.W.NN.txt"

    cleanAndWrite(ifile,ofile)

    ifile = "../../data/OFLexicon.results.notcast.weighted.withneutral"
    ofile = "../../data/OFL.NC.W.N.txt"

    cleanAndWrite(ifile,ofile)
    
##    ifile = "../../data/OFLexicon.results"
##    ofile = "../../data/OFL.txt"
##
##    cleanAndWrite(ifile, ofile)
##    
##    ifile = "../../data/OFLexicon.results.httpwwwsimplefilter"
##    ofile = "../../data/OFL-pp.txt"
##
##    cleanAndWrite(ifile, ofile)
##
##    ifile = "../../data/OFLexicon.results.NoPreparsing"
##    ofile = "../../data/OFL-no-pp.txt"
##
##    cleanAndWrite(ifile, ofile)
