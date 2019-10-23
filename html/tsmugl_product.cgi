#! /usr/bin/env python

import cgi, sys, os, os.path

sys.path.append("..")
#sys.path.append("../new-data/newNetCDFs2")
#sys.path.append("../new-data/newNetCDFs")
from Config import *

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
    data_dir = FORWARN_STD_MAX_MODIS_DIR
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


def extract_data_at_location(ncfilename, lon, lat):
  data = subprocess.check_output(['gdallocationinfo', ncfilename, '-wgs84', '-valonly', lon, lat])
  return data


def get_year_from_filename(filename):
  return filename.split('.')[1]


def get_nrt_data(year, lon, lat):
  data = []
  nrt_files = sorted(os.listdir(FORWARN_NRT_MAX_MODIS_DIR))
  for nrt_f in nrt_files:
    p = os.path.join(FORWARN_NRT_MAX_MODIS_DIR, nrt_f)
    d = extract_data_at_location(p, lon, lat)
    data.append(d)
  return data


output = []
for tsfile in FORWARN_MAX_MODIS_FILES:
    tsfile = get_tsfile_path(tsfile)
    if tsfile is False:
        continue

    ncfilename = tsfile + ".nc"

    data = extract_data_at_location(ncfilename, lon, lat)
    data = data.split("\n");
    data.remove('')
    if len(data) < 46:
      year = get_year_from_filename(tsfile)
      nrt_data = get_nrt_data(year, lon, lat)
      data.extend(nrt_data)

    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('.//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)

    formatString = "%s,%s"
    for i, v in enumerate(data):
        # Any value greater than 100 is invalid so skip it
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
