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

def main():
  try:
    output = get_full_output(lon, lat)
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


main()
