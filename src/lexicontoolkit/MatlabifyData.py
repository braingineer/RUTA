"""
author: gaurav kharkwal
date  : 20120302
about : Helper script to make data easier to import to Matlab.
        Removes '-' from the dates, replaces commas with tabs, and while
        so doing, computes the sentiment ratio (numPos/numNeg).

        Matlab will do the smoothing.
"""

def cleanAndWrite(ifile, ofile):
    """
    * helper function.
    * gets input and output file paths
    * opens and reads input, parses line, cleans data, computes...
        ... sentiment ratio, and outputs it to the output file. easy peasy.
    """

    ifh     = open(ifile)
    ilines  = ifh.readlines()
    ifh.close()

    ofh = open(ofile, 'w')

    counter = 1
    for il in ilines:
        counter += 1
        
        toks    = il.split(',')
        toks[0] = toks[0].replace('-','') # remove '-' from dates
        toks[2] = toks[2].strip()         # remove '\n' from last token

        # compute sentiment ratio
        toks.append(str(float(toks[1])/(float(toks[2]) + .1))) # .1 added for 0s

        newl = ('\t'.join(toks) + '\n')

        ofh.write(newl)
    ofh.close()


if __name__ == "__main__":
    ifile = "../../data/OFLexicon.results"
    ofile = "../../data/OFL.txt"

    cleanAndWrite(ifile, ofile)
    
    ifile = "../../data/OFLexicon.results.httpwwwsimplefilter"
    ofile = "../../data/OFL-pp.txt"

    cleanAndWrite(ifile, ofile)

    ifile = "../../data/OFLexicon.results.NoPreparsing"
    ofile = "../../data/OFL-no-pp.txt"

    cleanAndWrite(ifile, ofile)
