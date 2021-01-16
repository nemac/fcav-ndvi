
import os.path

# The year it all began
DATA_YEAR_START = 2003

# Default file extensions
DEFAULT_FILE_EXT_YR_MAX_STD = 'tif'
DEFAULT_FILE_EXT_8DAY_MAX_NRT = 'img'


## Helper files

# Note: prepending relative parent to paths since they
# are referenced from the html/ directory

# File containing all julian days for the year (zero-padded)
ALL_DAYS_PATH = '../all_product_days.txt'

# End dates for the ForWarn 2 24-day windows
NONLEAP_DATES_FILE = "../leap-dates.txt"
LEAP_DATES_FILE = "../nonleap-dates.txt"


# Symlinks to data directories

# Year maxes maxMODIS STD TIFs
STD_MAXES_BY_YR_DIR = "../data/std_maxes_by_year"

# Archive of all precursors (for fetching NRT data)
PRECURSOR_DIR = '../data/precursors'


# Helper functions

def get_yr_maxes_std_filename(yr, ext=DEFAULT_FILE_EXT_YR_MAX_STD):
  '''Returns the filename of the all-year maxes STD data file for a given year.'''
  return 'maxMODIS.{}.std.{}'.format(yr, ext)

def get_8day_max_nrt_filename(yr, jd, ext=DEFAULT_FILE_EXT_8DAY_MAX_NRT):
  '''Returns the filename of the NRT max filename for some 8-day window given year and day of year.'''
  return 'maxMODIS.{}.{}.nrt.{}'.format(yr, jd, ext)

def get_yr_maxes_std_path_for_yr(yr):
  '''Returns the path to the all-year maxes STD file for a given year.'''
  return os.path.join(STD_MAXES_BY_YR_DIR, get_yr_maxes_std_filename(yr))

