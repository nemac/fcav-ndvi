#!/usr/bin/env python3

import cgi, sys, os, os.path
import calendar
import subprocess, datetime

sys.path.append("..")
from config import *
from util import *

ALL_MODIS_JULIAN_DAYS = ("001", "009", "017", "025", "033", "041", "049", "057", "065", "073", "081", "089", "097", "105", "113", "121", "129", "137", "145", "153", "161", "169", "177", "185", "193", "201", "209", "217", "225", "233", "241", "249", "257", "265", "273", "281", "289", "297", "305", "313", "321", "329", "337", "345", "353", "361")

params = cgi.FieldStorage()
argstring = params["args"].value
arglist = argstring.split(",")
lon = arglist[1]
lat = arglist[2]

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


def scale_value(val):
  scaled = int(round((float(val)/250.0)*100))
  return scaled


def format_data_output(data, format_string, times):
  output = []
  for i, v in enumerate(data):
      if v.isnumeric():
          # Any value greater than 250 is invalid so skip it
          if int(v) > 250:
              continue
          if v == '0':
              val = v
          else:
              val = str(scale_value(v))
          output.append(format_datum(val, format_string, times[i]))
  return output


def format_datum(value, format_string, datestring):
  return format_string.format(datestring, value)


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
  format_string = "{},{},-9000"
  format_string_nrt = "{},-9000,{}"
  output = []
  for year in range(DATA_YEAR_START, int(get_current_year())+1):
    yr_maxes_std_path = get_yr_maxes_std_path_for_yr(year)
    datestrings = get_full_datestrings_for(year)

    # TODO
    # At the beginning of January the 2022 std file will not be ready yet
    # so we need a check here to continue if we're at the current year
    # and the file doesn't exist
    if int(get_current_year()) == int(year) and not os.path.exists(yr_maxes_std_path):
      # No std data for current year yet
      data = []
    else:
      data = run_gdallocationinfo(yr_maxes_std_path, lon, lat)
      data = data.split("\n");
      # the last element is an empty string so throw it out
      data = data[:-1]
      formatted_output = format_data_output(data, format_string, datestrings)
      output.extend(formatted_output)

   # if len(data) < 46 and int(year) != int(get_current_year()):
      # This is probably bad and means an std file for the previous year was not build properly
    #  print("ERROR Malformed year file {}".format(year))
    #  break

    # Check for available near-realtime data
    if len(data) < 46 and int(year) == int(get_current_year()):
      nrt_jd = ALL_MODIS_JULIAN_DAYS[len(data)]
      nrt_path = get_8day_max_nrt_path(year, nrt_jd)
      if os.path.exists(nrt_path):
        # Add a dummy point at the location of the final std point to connect
        # a line between the final STD point and the first NRT point
        # Dummy point becomes first NRT point in output
        if len(data):
          dummy_datestrings = [ datestrings[len(data)-1] ]
          dummy_point = format_data_output([ data[-1] ], format_string_nrt, dummy_datestrings)
        else:
          '''
          We're at the beginning of the year when no std file is available.
          In this case we'll manually create a dummy point by taking the last
          available std point and transforming it into an nrt-style point
          by shifting the location of the -9000, but keeping the same "value"

          Example output:
            ...
            20211226,58,-9000
            20220103,62,-9000 <-- At this point in code (this line is output[-1])
            20220103,-9000,62 <-- Dummy point (same "value" as previous line)
            20220108,-9000,52 <-- Final NRT point
          '''
          dummy_output = output[-1].split(',')
          dummy_point = [ ','.join([ dummy_output[0], dummy_output[2], dummy_output[1] ]) ]
        nrt_datum = run_gdallocationinfo(nrt_path, lon, lat)
        nrt_datum = str(int(nrt_datum.rstrip()))
        nrt_datestrings = [ datestrings[len(data)] ]
        formatted_nrt_data = format_data_output([nrt_datum], format_string_nrt, nrt_datestrings)
        output.extend(dummy_point)
        output.extend(formatted_nrt_data)
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
