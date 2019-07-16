#! /usr/bin/env python

#import cgi, sys
import sys

sys.path.append("../new-data/newNetCDFs2")
import Config

#from osgeo import gdal, osr
#from netCDF4 import Dataset
import subprocess
import xml.etree.ElementTree as ET

argstring = params["args"].value
arglist = argstring.split(",")
lat = arglist[1]
lon = arglist[2]

#lat = "35.2411"
#lon = "-76.8384"

def unsign8(x):
    if x >= 0:
        return x
    return 256 + x

class Template:
    def __init__(self, file):
        f = open(file, "r")
        self.contents = ""
        for line in f:
            self.contents = self.contents + line
        f.close
    def render(self, dict):
        return self.contents % dict

vlist = ""

output = []
for tsfile in Config.data_files: 
    tsfile = Config.data_dir + "/" + tsfile
    ncfilename = tsfile + ".nc"

    data = subprocess.check_output(
        ['gdallocationinfo', ncfilename, '-wgs84', '-valonly', lon, lat])
    data = data.split("\n");
    data.remove('')

    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)

    for i, v in enumerate(data):
        output.append("%s,%s" % (times[i],v))

muglTemplate = Template("../mugl.tpl.xml")

print "Content-type: text/xml\n"

print muglTemplate.render({
        'values' : "\n".join(output),
        'debug'  : "(x,y) = (%s,%s)" % (lon,lat)
      })
