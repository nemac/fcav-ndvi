#! /usr/bin/env python

import cgi, sys

#sys.path.append("../new-data/newNetCDFs2")
sys.path.append("..")
import Config

from osgeo import gdal, osr
from netCDF4 import Dataset
###from Scientific.IO.NetCDF import *
import xml.etree.ElementTree as ET

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

#params = cgi.FieldStorage()

pixel = [17823,7811]
#pixel = [17752,7811]

vlist = ""

#tsfile = Config.data_dir + "/" + Config.data_files[0]
tsfile = Config.data_dir + "/" + Config.data_files[7]
ncfilename = tsfile + ".nc"
ncfile = Dataset(ncfilename, "r")
band1 = ncfile.variables['Band1']
print band1
rlen = band1.shape[0]
r = 0
times = []
tptree = ET.parse(tsfile + ".ts.xml")
timepoints = tptree.findall('//timepoint')
for timepoint in timepoints:
    times.append(timepoint.text)
while r < rlen:
    b = unsign8(band1[r,pixel[1],pixel[0]]) 
    vlist = vlist + ("%s,%1d\n" % (times[r],b))
    r = r + 1

print vlist
