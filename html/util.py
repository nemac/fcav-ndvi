import sys, os, os.path, subprocess

sys.path.append("..")
from Config import *

import subprocess, datetime
import xml.etree.ElementTree as ET

ALL_DAYS_PATH = './all_product_days'

#lon=-80.21665953122013
#lat=35.563506726842284

def get_tsfile_path(tsfile):
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
        f.close()
    def render(self, dict):
        return self.contents % dict


def extract_data_at_location(ncfilename, lon, lat):
  data = subprocess.check_output(['gdallocationinfo', ncfilename, '-wgs84', '-valonly', lon, lat])
  return data


def get_year_from_tspath(tspath):
  return tspath.split('.')[-2]


def get_all_todo_days():
  days = []
  with open(ALL_DAYS_PATH) as f:
    for jd in f:
      days.append(jd.strip())
  return days


def get_todo_jdays():
  '''This function creates a list of julian days for product dates
  that may have available NRT data.'''
  days = get_all_todo_days() # TODO: test this!
  if not len(days):
    reset_todo_dates_file()
  today = datetime.datetime.today()
  today = today.strftime('%Y%j')
  today = datetime.datetime.strptime(today, '%Y%j')
  year = today.strftime('%Y')
  dates = map(lambda day: datetime.datetime.strptime('{0}{1}'.format(year, day), '%Y%j'), days)
  dates = filter(lambda d: d <= today - datetime.timedelta(days=8), dates)
  days = list(map(lambda d: d.strftime('%j'), dates))
  #dates = filter(lambda d: not max_file_exists('std', d), dates)
  return days



def get_nrt_data(year, lon, lat, num_std_points):
  '''Fetch NRT data points at a location for all days without STD data available.

  The number of data points at any location for an entire year is 46.
  There are usually going to be 8-day NRT files sitting around for older dates
  that already have STD data available. To prevent double-counting the data,
  we determine how many dates are possible to this point, remove the dates
  accounted for already by STD data, and search for any remaining NRT files
  that match the remaining dates.
  '''
  days = get_todo_jdays()
  # List of days not accounted for by STD data
  nrt_days = days[num_std_points:]
  # start/end indices for extracting the julian day from the NRT file
  jd_slice_start, jd_slice_end = 14, 17
  nrt_files = [ f for f in sorted(os.listdir(FORWARN_NRT_MAX_MODIS_DIR)) 
    if 'nrt' in f and year in f and f[jd_slice_start:jd_slice_end] in nrt_days ]
  data = []
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


#lon=-80.21665953122013
#lat=35.563506726842284

def get_full_output(lon, lat):
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

      # 46 data points in a year.
      # If there's less than 46 data points we're processing the current year.
      # Check for available near-realtime data
      #if len(data) < 46:
      #  num_std_points = len(data)
      #  year = get_year_from_tspath(tsfile)
      #  nrt_data = get_nrt_data(year, lon, lat, num_std_points)
      #  if len(nrt_data):
      #    format_string_nrt = "%s,-9000,%s"
      #    # Send num_std_points to offset the index of the times array so the NRT data
      #    # gets mapped to the correct timepoint
      #    formatted_output = format_data_output(nrt_data, format_string_nrt, times, num_std_points)
      #    # Add a dummy point at the location of the final std point to connect
      #    # a line between the final STD point and the first NRT point
      #    dummy_point = format_data_output([ data[-1] ], format_string_nrt, times, num_std_points-1)
      #    # Dummy point becomes first NRT point in output
      #    output.extend(dummy_point)
      #    output.extend(formatted_output)
  return output
