#!/usr/bin/env python

import cgi, sys, os, os.path
import calendar

sys.path.append("..")
from config import *

import subprocess, datetime


params = cgi.FieldStorage()
argstring = params["args"].value
arglist = argstring.split(",")
lon = arglist[1]
lat = arglist[2]


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


def run_gdallocationinfo(path, lon, lat):
  data = subprocess.check_output(['gdallocationinfo', path, '-wgs84', '-valonly', lon, lat])
  return data


def get_all_todo_days():
  days = []
  with open(ALL_DAYS_PATH) as f:
    for jd in f:
      days.append(jd.strip())
  return days


def get_current_year():
  today = datetime.datetime.today()
  year = today.strftime('%Y')
  return year


def get_possible_data_jdays_this_year():
  '''Return a list of julian days for which data may exist for this year.'''
  days = get_all_todo_days()
  today = datetime.datetime.today()
  today = today.strftime('%Y%j')
  today = datetime.datetime.strptime(today, '%Y%j')
  year = today.strftime('%Y')
  dates = map(lambda day: datetime.datetime.strptime('{0}{1}'.format(year, day), '%Y%j'), days)
  dates = filter(lambda d: d <= today - datetime.timedelta(days=8), dates)
  days = list(map(lambda d: d.strftime('%j'), dates))
  return days


def get_nrt_data(year, lon, lat, num_std_points):
  '''Fetch NRT data points at a location for all days without STD data available.

  The number of data points at any location for an entire year is 46.
  Determine how many dates are possible to this point, remove the dates
  accounted for already by STD data, and search for any remaining NRT files
  that match the remaining dates.
  '''
  days = get_possible_data_jdays_this_year()
  # List of days not accounted for by STD data
  nrt_days = days[num_std_points:]
  nrt_paths = [ os.path.join(PRECURSOR_DIR, jd, get_8day_max_nrt_filename(get_current_year(), jd)) for jd in nrt_days ]
  nrt_paths = list(sorted(filter(os.path.exists, nrt_paths)))
  data = []
  for nrt_path in nrt_paths:
    d = run_gdallocationinfo(nrt_path, lon, lat)
    data.append(d)
  return data


def scale_value(val):
  val = float(val)
  scaled = (val/250.0)*100
  return scaled


def format_data_output(data, format_string, times, time_index_offset=0):
  output = []
  for i, v in enumerate(data):
      # Any value greater than 250 is invalid so skip it
      if int(v) > 250:
          continue
      if v == '0':
          val = v
      else:
          val = str(scale_value(v))
      output.append(format_string % (times[time_index_offset+i],val))
  return output


def get_full_datestrings_for(year):
    is_leap = calendar.isleap(int(year))
    
    if is_leap:
      f = open(NONLEAP_DATES_FILE)
    else:
      f = open(LEAP_DATES_FILE)
    partial_datestrings = [ line.strip() for line in f ]
    f.close()
    # The final datestring falls on the following year so build separately
    full_datestrings = [ '{}{}'.format(str(year), d) for d in partial_datestrings[:-1] ]
    full_datestrings.append('{}{}'.format(str(int(year)+1), partial_datestrings[-1]))
    return full_datestrings


output = []
for year in range(DATA_YEAR_START, int(get_current_year())+1):
    yr_maxes_std_path = get_yr_maxes_std_path_for_yr(year)

    data = run_gdallocationinfo(yr_maxes_std_path, lon, lat)
    data = data.split("\n");
    data.remove('')

    datestrings = get_full_datestrings_for(year)
    format_string = "%s,%s,-9000"
    formatted_output = format_data_output(data, format_string, datestrings)
    output.extend(formatted_output)

    if len(data) < 46 and year != get_current_year():
      # This is probably bad and means an std file for the previous year was not build properly
      pass

    # Check for available near-realtime data
    if len(data) < 46 and year == get_current_year():
      num_std_points = len(data)
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
