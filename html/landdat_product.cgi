#! /usr/bin/env python

import cgi, sys

sys.path.append("..")
#sys.path.append("../new-data/newNetCDFs2")
sys.path.append("../new-data/newNetCDFs")
import Config

#from osgeo import gdal, osr
#from netCDF4 import Dataset
import subprocess
import xml.etree.ElementTree as ET

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
for tsfile in Config.data_files: 
    tsfile = Config.data_dir + "/" + tsfile
    ncfilename = tsfile + ".nc"

    data = subprocess.check_output(
        ['gdallocationinfo', ncfilename, '-wgs84', '-valonly', lat, lon])
    data = data.split("\n");
    data.remove('')

    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)

    for i, v in enumerate(data):
        output.append("%s,%s" % (times[i],v))

print 'Content-type: application/json\n'
print output
