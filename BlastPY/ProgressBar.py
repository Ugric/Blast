import sys
import time
from humanfriendly import format_timespan
from .accurateETA import accurateETA


def progressbar(it, prefix="", size=30, file=sys.stdout):
    count = len(it)
    lasttime = time.time()
    starttime = time.time()
    pscount = 0
    eta = 0
    j = 0
    ps = 0
    nowps = 0
    x = int(size*j/count)
    formats = "%s%s%s %i/%i - %s - %s - %sps" % (prefix, "▓"*x, "░"*(
        size-x), j, count, format_timespan(round(lasttime-starttime)), format_timespan(eta), ps)
    lastformatlength = len(formats)
    formats += "\r"
    file.write(formats)
    file.flush()
    for i, item in enumerate(it):
        yield item
        pscount += 1
        nowps += 1
        j = i+1
        x = int(size*j/count)
        currenttime = time.time()
        difference = currenttime-lasttime
        if difference >= 0.5:
            ps = round((j)/(currenttime-starttime), 1)
            eta = int(accurateETA(
                currenttime-starttime, count, j, (j)/(currenttime-starttime)))
            nowps = 0
            lasttime = time.time()
        formats = "%s%s%s %i/%i - %s - %s - %sps" % (prefix, "▓"*x, "░"*(
            size-x), j, count, format_timespan(round(lasttime-starttime)), format_timespan(eta), ps)
        formatdifferance = lastformatlength-len(formats)
        lastformatlength = len(formats)
        formats += (" "*(formatdifferance if formatdifferance > 0 else 0))+"\r"
        file.write(formats)
        file.flush()
    file.write("\n\n")
    file.flush()
