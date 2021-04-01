#! /usr/bin/env python

import cgi, sys, os, os.path

sys.path.append("..")
from Config import *

import subprocess, datetime
import xml.etree.ElementTree as ET

from util import *

params = cgi.FieldStorage()
argstring = params["args"].value
arglist = argstring.split(",")
lon = arglist[1]
lat = arglist[2]

# For testing purposes, not used by the viewer
if 'values_only' in params and params['values_only'].value.lower() == 'true':
  values_only = True
else:
  values_only = False

muglTemplate = Template("../mugl.tpl.xml")

output = get_full_output(lon, lat)

if not values_only:
  print "Content-type: text/xml\n"
  print muglTemplate.render({
          'values' : "\n".join(output),
          'debug'  : "(x,y) = (%s,%s)" % (lon,lat)
        })
else:
  print "Content-type: text/plain\n"
  print "\n".join(output)

