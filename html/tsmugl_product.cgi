#!/usr/bin/env python3

import cgi, sys, os, os.path
import calendar
import subprocess, datetime

sys.path.append("..")
from config import *

ALL_MODIS_JULIAN_DAYS = ("001", "009", "017", "025", "033", "041", "049", "057", "065", "073", "081", "089", "097", "105", "113", "121", "129", "137", "145", "153", "161", "169", "177", "185", "193", "201", "209", "217", "225", "233", "241", "249", "257", "265", "273", "281", "289", "297", "305", "313", "321", "329", "337", "345", "353", "361")

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
  path = os.path.realpath(path)
  # CompletedSubprocess
  #c = f'gdallocationinfo -wgs84 -valonly {path} {lon} {lat}'
  c = [f'gdallocationinfo -wgs84 -valonly {path} {lon} {lat}']
  result = subprocess.run(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  msg = 'STDOUT: {}\n\n'.format(result.stdout.decode('utf-8'))
  msg += 'STDERR: {}\n\n'.format(result.stderr.decode('utf-8'))
  if result.returncode > 0:
    raise Exception(msg)
  return result.stdout.decode('utf-8')


def get_current_year():
  today = datetime.datetime.today()
  year = today.strftime('%Y')
  return year


def get_possible_data_jdays_this_year():
  '''Return a list of julian days for which data may exist for this year.'''
  days = ALL_MODIS_JULIAN_DAYS
  today = datetime.datetime.today()
  today = today.strftime('%Y%j')
  today = datetime.datetime.strptime(today, '%Y%j')
  year = today.strftime('%Y')
  dates = map(lambda day: datetime.datetime.strptime('{0}{1}'.format(year, day), '%Y%j'), days)
  dates = filter(lambda d: d <= today - datetime.timedelta(days=8), dates)
  days = list(map(lambda d: d.strftime('%j'), dates))
  return days


def get_todo_dates(self):
  '''Get a list of potential dates for which ForWarn 2 products may be built.

  Return a list of MODIS product dates in the past two years for which:

  1. Enough time has passed that NRT data for that date may be available.
  2. A complete set of ForWarn 2 products does not exist.

  In theory NRT data should be available for these dates, but it's possible the data is late.
  '''
  all_days = ALL_FW2_JULIAN_DAYS
  today = datetime.datetime.today()
  today_year = today.strftime('%Y')
  last_year = str(int(today_year) - 1)
  this_year_todo_dates = map(lambda jd: self.get_datetime_for_year_jd(today_year, jd), all_days)
  last_year_todo_dates = map(lambda jd: self.get_datetime_for_year_jd(last_year, jd), all_days)
  potential_this_year_todo_dates = self.filter_unavailable_modis_dates(this_year_todo_dates)
  potential_last_year_todo_dates = self.filter_unavailable_modis_dates(last_year_todo_dates)
  potential_todo_dates = potential_this_year_todo_dates + potential_last_year_todo_dates
  potential_todo_date_dicts = list(map(self.get_year_jd_config_for_datetime, potential_todo_dates))
  todo_dates = list(filter(lambda d: not self.is_ok(d), potential_todo_date_dicts))
  return todo_dates


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
    d = str(int(d.rstrip()))
    data.append(d)
  return data


def scale_value(val):
  scaled = int(round((float(val)/250.0)*100))
  return scaled


def format_data_output(data, format_string, times):
  output = []
  for i, v in enumerate(data):
      # Any value greater than 250 is invalid so skip it
      if int(v) > 250:
          continue
      if v == '0':
          val = v
      else:
          val = str(scale_value(v))
      output.append(format_datum(format_string, times[i], val))
  return output


def format_datum(value, format_string, datestring):
  return format_string % (datestring, value)


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



def get_full_output():
  output = []
  for year in range(DATA_YEAR_START, int(get_current_year())+1):
      yr_maxes_std_path = get_yr_maxes_std_path_for_yr(year)

      data = run_gdallocationinfo(yr_maxes_std_path, lon, lat)
      data = data.split("\n");
      # the last element is an empty string so throw it out
      data = data[:-1]
      datestrings = get_full_datestrings_for(year)
      format_string = "%s,%s,-9000"
      formatted_output = format_data_output(data, format_string, datestrings)
      output.extend(formatted_output)

      if len(data) < 46 and int(year) != int(get_current_year()):
        # This is probably bad and means an std file for the previous year was not build properly
        print("ERROR Malformed year file {}".format(year))
        break

      # Check for available near-realtime data
      if len(data) < 46 and int(year) == int(get_current_year()):
        nrt_jd = ALL_MODIS_JULIAN_DAYS[len(data)]
        nrt_path = get_8day_max_nrt_path(year, nrt_jd)
        if os.path.exists(nrt_path):
          nrt_datum = run_gdallocationinfo(nrt_path, lon, lat)
          nrt_datum = str(int(d.rstrip()))
          data.append(d)
           
          
        
        num_std_points = len(data)
        nrt_data = get_nrt_data(year, lon, lat, num_std_points)
        format_string_nrt = "%s,-9000,%s"
        # Send num_std_points to offset the index of the datestrings array so the NRT data
        # gets mapped to the correct timepoint
        formatted_output = format_data_output(nrt_data, format_string_nrt, datestrings, num_std_points)
        # Add a dummy point at the location of the final std point to connect
        # a line between the final STD point and the first NRT point
        dummy_point = format_data_output([ data[-1] ], format_string_nrt, datestrings, num_std_points-1)
        # Dummy point becomes first NRT point in output
        output.extend(dummy_point)
        output.extend(formatted_output)
  return output


try:
  output = get_full_output()
  muglTemplate = Template("../mugl.tpl.xml")
  print("Content-type: text/xml\n")
  print(muglTemplate.render({
          'values' : "\n".join(output),
          'debug'  : "(x,y) = (%s,%s)" % (lon,lat)
        }))
except Exception as e:
  print('Content-type: text/plain')
  print()
  import traceback
  traceback.print_tb(e.__traceback__)
  print(str(e))


