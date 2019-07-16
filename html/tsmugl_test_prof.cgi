#! /usr/bin/env python

# tsmugl.cgi 'args=bigfile,-8359100,5105690'

import cgi, sys

sys.path.append("..")
import Config

from osgeo import gdal, osr
from netCDF4 import Dataset
###from Scientific.IO.NetCDF import *
import xml.etree.ElementTree as ET

webMercatorWKT = """PROJCS["WGS_1984_Web_Mercator",GEOGCS["GCS_WGS_1984_Major_Auxiliary_Sphere",DATUM["WGS_1984_Major_Auxiliary_Sphere",SPHEROID["WGS_1984_Major_Auxiliary_Sphere",6378137.0,0.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_1SP"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["latitude_of_origin",0.0],UNIT["Meter",1.0]]"""

def coords_to_pixel(X,Y,geoTransform):
    det = geoTransform[1]*geoTransform[5] - geoTransform[2]*geoTransform[4]
    X = X - geoTransform[0]
    Y = Y - geoTransform[3]
    x = ( geoTransform[5] * X - geoTransform[2] * Y) / det
    y = (-geoTransform[4] * X + geoTransform[1] * Y) / det
    return [int(x),int(y)]

def src_coords_to_pixel(x,y,ncfile):
    source_srs     = osr.SpatialReference(webMercatorWKT)  # (x,y) are in WebMercator
    ncDataSet      = gdal.Open( ncfile, gdal.GA_ReadOnly )
    target_srs     = osr.SpatialReference(ncDataSet.GetProjection())
    transformation = osr.CoordinateTransformation(source_srs, target_srs)
    transformedxy  = transformation.TransformPoint(x,y)
    geoTransform   = ncDataSet.GetGeoTransform()
    pixel          = coords_to_pixel(transformedxy[0], transformedxy[1], geoTransform)
    return pixel

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

params = cgi.FieldStorage()

#argstring = params["args"].value
#arglist = argstring.split(",")
#tsfile_product = arglist[0]
#X = float(arglist[1])
#Y = float(arglist[2])
#-76.8384 35.2411
#-8553301.7636339,4197003.6198779
X = float(-8553301.7636339)
Y = float(4197003.6198779)

pixel = src_coords_to_pixel(X,Y,Config.data_dir + "/" + Config.data_files[0]+".nc")

vlist = ""
for tsfile in Config.data_files: 
    tsfile = Config.data_dir + "/" + tsfile
    ncfilename = tsfile + ".nc"
    #ncfile = NetCDFFile(ncfilename, "r")    
    ncfile = Dataset(ncfilename, "r") # changed!
    band1 = ncfile.variables['Band1']
    rlen = band1.shape[0]
    ylen = band1.shape[1]
    xlen = band1.shape[2]
    r = 0
    times = []
    tptree = ET.parse(tsfile + ".ts.xml")
    timepoints = tptree.findall('//timepoint')
    for timepoint in timepoints:
        times.append(timepoint.text)
    while r < rlen:
        #b = unsign8(band1[r,pixel[1],pixel[0]][0])
        b = unsign8(band1[r,pixel[1],pixel[0]]) 
        vlist = vlist + ("%s,%1d\n" % (times[r],b))
        r = r + 1

muglTemplate = Template("../mugl.tpl.xml")

print "Content-type: text/xml\n"

print muglTemplate.render({
        'values' : vlist,
        'debug'  : "(x,y) = (%s,%s)" % (pixel[0],pixel[1])
      })
