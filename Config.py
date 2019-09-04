# This file, "Config.py.template", is a template for creating
# "Config.py".
# 
# A deployed/production copy of this application should contain a 
# file named "Config.py" which should be edited to contain
# settings that are appropriate for that deployed copy.
# 
# Note that the git repository only contains "Config.py.template",
# NOT "Config.py".  When deploying a copy of this application,
# you should make a copy of "Config.py.template" named "Config.py",
# and edit it to contain settings that are correct for that
# deployed copy.

# ForWarn 2 NetCDFs
FORWARN_MAX_MODIS_DIR = "../data/forwarn_archive"

# LanDAT NDVI files from Joe Spruce
LANDAT_NDVI_ARCHIVE_DIR = "../data/landat/ndvi_archive"

LANDAT_NDVI_FILES = [
  'land2000',
  'land2001',
  'land2002',
  'land2003',
  'land2004',
  'land2005',
  'land2006',
  'land2007',
  'land2008',
  'land2009',
  'land2010',
  'land2011',
  'land2012',
  'land2013',
  'land2014',
  'land2015',
  'land2016',
  'land2017'
]

NONLEAP_DATES_FILE = "../data/dates_nonleap.txt"

LEAP_DATES_FILE = "../data/dates_leap.txt"

### `data_files` should be an array which specifies the data files in
### `data_dir`.  Each element in the `data_files` array should be a
### string which is name of a NetCDF file in data_dir, WITHOUT the
### final `.nc` suffix.
### 
### For each element in this array, in addition to the `.nc` file, there
### should also be a file ending in `.ts.xml` in `data_dir`, giving
### the dates associated with the data records in the `.nc` file.
FORWARN_MAX_MODIS_FILES = [
       'maxMODIS.2003.std',
       'maxMODIS.2004.std',
       'maxMODIS.2005.std',
       'maxMODIS.2006.std',
       'maxMODIS.2007.std',
       'maxMODIS.2008.std',
       'maxMODIS.2009.std',
       'maxMODIS.2010.std',
       'maxMODIS.2011.std',
       'maxMODIS.2012.std',
       'maxMODIS.2013.std',
       'maxMODIS.2014.std',
       'maxMODIS.2015.std',
       'maxMODIS.2016.std',
       'maxMODIS.2017.std',
       'maxMODIS.2018.std'
]
