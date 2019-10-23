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

# Max MODIS STD NetCDFs
FORWARN_STD_MAX_MODIS_DIR = "../data/forwarn_archive"

# Max MODIS NRT NetCDFs (8-day)
FORWARN_NRT_MAX_MODIS_DIR = "/fsdata4/forwarn2_products/forwarn2_build_dev/netcdf/nrt"

# LanDAT NDVI files from Joe Spruce
LANDAT_NDVI_ARCHIVE_DIR = "../data/landat_archive"

LANDAT_NDVI_FILES = [
  'land2000.tif',
  'land2001.tif',
  'land2002.tif',
  'land2003.tif',
  'land2004.tif',
  'land2005.tif',
  'land2006.tif',
  'land2007.tif',
  'land2008.tif',
  'land2009.tif',
  'land2010.tif',
  'land2011.tif',
  'land2012.tif',
  'land2013.tif',
  'land2014.tif',
  'land2015.tif',
  'land2016.tif',
  'land2017.tif'
]


# These dates are the end dates for the 24-day windows
NONLEAP_DATES_FILE = "../leap-dates.txt"
LEAP_DATES_FILE = "../nonleap-dates.txt"

# These dates are the center dates for the 24-day windows
LANDAT_LEAP_DATES_FILE = "../center-leap-dates.txt"
LANDAT_NONLEAP_DATES_FILE = "../center-nonleap-dates.txt"


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
       'maxMODIS.2018.std',
       'maxMODIS.2019.std'
]
