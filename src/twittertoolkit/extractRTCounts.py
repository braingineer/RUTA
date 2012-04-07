"""
FILENAME: ExtractRTCounts.PY
AUTHOR  : Gaurav Kharkwal
DATE    : 2012/06/04

ABOUT   :
        1) read RT "graphs" (csv files with "master", "slave", and "message")
        2) make dict with counts of "master" RTs
        3) output dict to a file
        4) sip tea
"""

import pickle

if __name__ == "__main__":
##    gFiles = ["tweets2009-06_mentionGraph.csv",
##              "tweets2009-07_mentionGraph.csv",
##              "tweets2009-08_mentionGraph.csv",
##              "tweets2009-09_mentionGraph.csv",
##              "tweets2009-10_mentionGraph.csv",
##              "tweets2009-11_mentionGraph.csv",
##              "tweets2009-12_mentionGraph.csv"]

##    gFiles = ["tweets2009-06-clipped_mentionGraph.txt"]

    RTDict = dict()
    for gFile in gFiles:
        gfh = open(gFile)

        counter = 0
        while True:
            lines = gfh.readlines(1000000)
            if not lines:
                break

            for line in lines:
                if line:
                    master = line.split(",")[0]
                    if master not in RTDict:
                        RTDict[master] = [1]
                    else:
                        RTDict[master][0] += 1

            counter += 1000000
            print gFile, counter

        gfh.close()

    maxVal = 0
    for k,v in RTDict.items():
        if v[0] > maxVal:
            maxVal = v[0]

    for k,v in RTDict.items():
        RTDict[k].append(RTDict[k][0]*1.0/maxVal)
    
    ofh = open("RTCounts.csv", "w")
    for master in sorted(RTDict, key=RTDict.get, reverse=True):
        ofh.write(master.strip()+","+str(RTDict[master][0])+","+str(RTDict[master][1])+"\n")
    ofh.close()

    pickle.dump(RTDict, open("RTCounts.pkl", "wb"))
