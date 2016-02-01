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

### 'data_dir' is the directory where the data files are located
data_dir = "../data"

### `data_files` should be an array which specifies the data files in
### `data_dir`.  Each element in the `data_files` array should be a
### string which is name of a NetCDF file in data_dir, WITHOUT the
### final `.nc` suffix.
### 
### For each element in this array, in addition to the `.nc` file, there
### should also be a file ending in `.ts.xml` in `data_dir`, giving
### the dates associated with the data records in the `.nc` file.
data_files = ["MCD13.A2000.unaccum",
              "MCD13.A2001.unaccum",
              "MCD13.A2002.unaccum",
              "MCD13.A2003.unaccum",
              "MCD13.A2004.unaccum",
              "MCD13.A2005.unaccum",
              "MCD13.A2006.unaccum",
              "MCD13.A2007.unaccum",
              "MCD13.A2008.unaccum",
              "MCD13.A2009.unaccum",
              "MCD13.A2010.unaccum",
              "MCD13.A2011.unaccum",
              "MCD13.A2012.unaccum",
              "MCD13.A2013.unaccum",
			  "MCD13.A2014.unaccum"
              ]
