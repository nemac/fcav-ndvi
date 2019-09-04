#! /usr/bin/env python

import cgi, sys

sys.path.append("..")
from Config import *

#from osgeo import gdal, osr
#from netCDF4 import Dataset
import subprocess
import xml.etree.ElementTree as ET

import calendar

params = cgi.FieldStorage()
argstring = params["args"].value
arglist = argstring.split(",")
lat = arglist[0]
lon = arglist[1]

#lon = "35.2411"
#lat = "-76.8134"

def unsign8(x):
    if x >= 0:
        return x
    return 256 + x

output = []
for filename in LANDAT_NDVI_FILES: 
    tsfile = LANDAT_NDVI_ARCHIVE_DIR + "/" + filename

    data = subprocess.check_output(
        ['gdallocationinfo', tsfile, '-wgs84', '-valonly', lat, lon])
    data = data.split("\n");
    data.remove('')

    times = []
    # Extract the year from the filename
    year = int(filename[4:8])
    dates_file = LEAP_DATES_FILE if calendar.isleap(year) else NONLEAP_DATES_FILE
    f = open(dates_file)
    dates = [ x.rstrip('\n') for x in f.readlines() ]
    f.close()

    times = [ '' + str(year) + x for x in dates ]
    # The last timepoint rolls over to the next year
    times[-1] = '' + str(year+1) + times[-1][4:]

    for i, v in enumerate(data):
        output.append("%s,%s" % (times[i],v))

print 'Content-type: application/json\n'
print output
