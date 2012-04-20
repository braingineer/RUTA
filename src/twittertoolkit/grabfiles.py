
def getFiles():
	import commands
	path = "/media/OS/twitterdata/"
	
	months = commands.getoutput("ls %s" % path).split("\n")[:-1]
	allfilehandlers=[]
	
	for m in months:
		days = commands.getoutput("ls %s/%s" % (path, m)).split("\n")
		for day in days:
			allfilehandlers.append(open("%s/%s/%s" % (path, m, day)))
			#print "%s/%s/%s" % (path, m, day)
	return allfilehandlers


print len(getFiles())