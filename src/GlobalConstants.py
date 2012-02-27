BASE_DIR = "/home/brian/TwitterSpring2012/RUTA/"
VERBOSE = True
LOG_DIR = "logs"
import time

def LOG(outfile, line):
    outfile.write(line)
    
def GEN_LOG_FILENAME_WITH_TIMESTAMP(stub):
    t=time.localtime()
    timestamp = "%s-%s-%s_%s.%s" % (t.tm_mon, t.tm_mday, t.tm_mday, t.tm_hour, t.tm_min)
    return "%s.%s" % (stub, timestamp)
