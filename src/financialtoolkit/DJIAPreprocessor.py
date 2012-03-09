#!/usr/bin/python

# !! Not sure if this file should be here
# It's a "cleaner" script for the Dow-Jones data.
# To run it, download the DJIA data file from Yahoo! Finance and update the
# path variable below

# CAUTION: relative path
PATH = "../../data/";

f = open(PATH+'DJIA.csv');

# the file's in reverse chronological order, so act accordingly
condition = True
lines = f.readlines();

observations = [];

for i in xrange(1,len(lines)):
    if i+3 >= len(lines):
        break

    date  = lines[i].split(',')[0].strip().replace('-','');
    opVal = lines[i].split(',')[6].strip();
    feat3 = lines[i+1].split(',')[6].strip();
    feat2 = lines[i+2].split(',')[6].strip();
    feat1 = lines[i+3].split(',')[6].strip();

    observations.append(date+"\t"+feat1+"\t"+feat2+"\t"+feat3+"\t"+opVal+"\n");

f.close();

observations.reverse();

trainSize = int(.9 * len(observations));

f = open(PATH+'DJIA.txt','w')
f.write("".join(observations))
f.close()

f = open(PATH+'DJIA_train.txt', 'w');
f.write("".join(observations[:trainSize]));
f.close();

f = open(PATH+'DJIA_test.txt', 'w');
f.write("".join(observations[trainSize:]));
f.close();
