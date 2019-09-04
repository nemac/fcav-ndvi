#! /usr/bin/env python

import cgi, sys, os, os.path

sys.path.append("..")
#sys.path.append("../new-data/newNetCDFs2")
#sys.path.append("../new-data/newNetCDFs")
import Config

#from osgeo import gdal, osr
#from netCDF4 import Dataset
import subprocess
import xml.etree.ElementTree as ET

params = cgi.FieldStorage()
argstring = params["args"].value
arglist = argstring.split(",")
lon = arglist[1]
lat = arglist[2]

def get_tsfile_path (tsfile):
    data_dir = Config.FORWARN_MAX_MODIS_DIR
    path = os.path.join(data_dir, tsfile)
    if os.access(path + '.nc', os.F_OK):
        return path
    else:
        return False

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

output = []
for tsfile in Config.FORWARN_MAX_MODIS_FILES:
    tsfile = get_tsfile_path(tsfile)
    if tsfile is False:
        continue

    ncfilename = tsfile + ".nc"

    data = subprocess.check_output(
        ['gdallocationinfo', ncfilename, '-wgs84', '-valonly', lon, lat])
    data = data.split("\n");
    data.remove('')

    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('.//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)

    formatString = "%s,%s"
    for i, v in enumerate(data):
        # Rescale the value from 0-250 to 0-100
        if int(v) > 100:
            continue
        if v == '0':
            val = v
        else:
            val = str(int(v))
        output.append(formatString % (times[i],val))

muglTemplate = Template("../mugl.tpl.xml")

print "Content-type: text/xml\n"

print muglTemplate.render({
        'values' : "\n".join(output),
        'debug'  : "(x,y) = (%s,%s)" % (lon,lat)
      })
