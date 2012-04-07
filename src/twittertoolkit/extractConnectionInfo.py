"""
FILENAME: ExtractConnectionInfo.PY
AUTHOR  : Gaurav Kharkwal
DATE    : 2012/06/04

ABOUT   :
        1) read tweet data
        2) create RT "graphs"
            2.1) basically csv files with "master", "slave", and "message"
        3) sip tea
"""

if __name__ == "__main__":
##    dFiles = ["tweets2009-06.txt",
##              "tweets2009-07.txt",
##              "tweets2009-08.txt",
##              "tweets2009-09.txt",
##              "tweets2009-10.txt",
##              "tweets2009-11.txt",
##              "tweets2009-12.txt"]

    
##    dFiles = ["tweets2009-06-clipped.txt"]
    
    for dFile in dFiles:
        dfh = open(dFile)

        oFileName = dFile.split(".")[0]+"_mentionGraph.csv"
        ofh = open(oFileName, "w")
        
        # loop over lines
        # ugh, it'll take ages
        counter = 0
        while True:
            lines = dfh.readlines(1000000)
            if not lines:
                break

            mentionEdges = []
            for i in xrange(len(lines)):
                if lines[i].strip() and lines[i].split(None, 1)[0] == "W":
                    # reading a message, we are
                    goodMsg = False
                    if "RT" in lines[i] and "@" in lines[i]:
                        # useful, this line is
                        message = lines[i].split(None,1)[1].strip()
                        
                        # not a good way, this is
                        tokens = message.split()
                        for j in xrange(len(tokens)):
                            if tokens[j] == "RT" and j < len(tokens)-1 and "@" in tokens[j+1]:
                                master = ""
                                if tokens[j+1] == "@" and j+2 < len(tokens):
                                    master = tokens[j+2]
                                else:
                                    master = tokens[j+1].split("@")[-1].split(":")[0]

                                if master:
                                    goodMsg = True
                                break

                        # get the "slave" name, now you should
                        tokens = lines[i-1].split("/")
                        slave = tokens[-1].strip()

                        if goodMsg:
                            mentionEdges.append([master, slave, message])

            # write the edges to file, you should
            for mentionEdge in mentionEdges:
                ofh.write(','.join(mentionEdge)+"\n")

            # clear mentionEdge now
            del mentionEdges

            # feedback, you should give
            counter += 1000000
            print dFile, counter
        
        # close files, you should
        ofh.close()
        dfh.close()
