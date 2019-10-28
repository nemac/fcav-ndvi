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


def get_nrt_data(year, lon, lat, num_std_points):
  '''
  We want the number of data points for the year to add up to 46.
  In case there are old NRT files, we want to only include the latest data
  that doesn't double-count for included STD data. We use negative indices
  to count backwards from the end of the list of files (where the latest data is)
  and take a slice to the end of the list to get the nrt data we want
  '''
  data = []
  nrt_files = sorted(os.listdir(FORWARN_NRT_MAX_MODIS_DIR))
  num_nrt_points = 46 - num_std_points
  nrt_files = nrt_files[-num_nrt_points:]
  for nrt_f in nrt_files:
    p = os.path.join(FORWARN_NRT_MAX_MODIS_DIR, nrt_f)
    d = extract_data_at_location(p, lon, lat)
    data.append(d)
  return data


def format_data_output(data, format_string, times, time_index_offset=0):
  output = []
  for i, v in enumerate(data):
      # Any value greater than 100 is invalid so skip it
      if int(v) > 100:
          continue
      if v == '0':
          val = v
      else:
          val = str(int(v))
      output.append(format_string % (times[time_index_offset+i],val))
  return output


output = []
for tsfile in FORWARN_MAX_MODIS_FILES:
    tsfile = get_tsfile_path(tsfile)
    if tsfile is False:
        continue

    ncfilename = tsfile + ".nc"

    data = extract_data_at_location(ncfilename, lon, lat)
    data = data.split("\n");
    data.remove('')

    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('.//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)

    format_string = "%s,%s,-9000"
    formatted_output = format_data_output(data, format_string, times)
    output.extend(formatted_output)

    # If there's less than 46 data points we're at the current year
    # Check for available near-realtime data
    if len(data) < 46:
      num_std_points = len(data)
      year = get_year_from_filename(tsfile)
      nrt_data = get_nrt_data(year, lon, lat, num_std_points)
      format_string_nrt = "%s,-9000,%s"
      # Send num_std_points to offset the index of the times array so the NRT data
      # gets mapped to the correct timepoint
      formatted_output = format_data_output(nrt_data, format_string_nrt, times, num_std_points)
      # Add a dummy point at the location of the final std point to connect
      # a line between the final STD point and the first NRT point
      dummy_point = format_data_output([ data[-1] ], format_string_nrt, times, num_std_points-1)
      # Dummy point becomes first NRT point in output
      output.extend(dummy_point)
      output.extend(formatted_output)


muglTemplate = Template("../mugl.tpl.xml")

print "Content-type: text/xml\n"

print muglTemplate.render({
        'values' : "\n".join(output),
        'debug'  : "(x,y) = (%s,%s)" % (lon,lat)
      })
