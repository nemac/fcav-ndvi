#! /usr/bin/env python

# This script converts weekly eMODIS data to netcdf files
# and concatenates these files into a netcdf for the current year.
# This data is considered "provisional" and is useful for displaying
# relatively real-time NDVI data when temporally processed MODIS NetCDFs
# containing data for an entire year are not yet available.
#
# Author: Matthew Geiger
#

import sys, os, glob, datetime, calendar, logging
import xml.etree.ElementTree as ET


#### Settings
dir_weekly_emodis_tiffs = '/fsdata1/fsdata/efetac_nasa/X_NDVI_MAX_EMODIS/'

dir_years_ndvi_netcdf = os.getcwd() + '/data/'
dir_weekly_emodis_netcdf = dir_years_ndvi_netcdf + 'emodis_weekly/'

year_netcdf_filename_template = 'MCD13.A{0}.unaccum.RAW.ONGOING'
#### End Settings

def get_ongoing_year_from_netcdf_path (path):
  return int(path.split('/')[-1].split('.')[1][1:])


def make_timepoint_xml_file (year):
  year = int(year)
  ref_year = year - 1
  while is_leap_year(year) is not is_leap_year(ref_year):
    ref_year = ref_year - 1
  glob_ref_path = glob.glob(dir_years_ndvi_netcdf + '*'+str(ref_year) + '*.ts.xml')
  ref_path = glob_ref_path[0]
  new_path = dir_years_ndvi_netcdf + year_netcdf_filename_template.format(str(year)) + '.ts.xml'
  ref_tree = ET.parse(ref_path)
  timepoints = ref_tree.findall('.//timepoint')
  for timepoint in timepoints:
    timepoint.text = str(year) + timepoint.text[4:]
  ref_tree.write(new_path)


def ongoing_file_exists ():
  glob_path = glob.glob(dir_years_ndvi_netcdf + "*ONGOING.nc")
  if (len(glob_path) > 0):
    return True
  else:
    return False


def get_path_to_ongoing_year_emodis_netcdf ():
  glob_path = glob.glob(dir_years_ndvi_netcdf + "*ONGOING.nc")
  if (len(glob_path) > 0):
    return glob_path[0]
  else:
    # Ongoing file is missing -- assume we're starting new year
    # Make a path string to new year based on the latest year
    glob_netcdfs = glob.glob(dir_years_ndvi_netcdf + "*.nc")
    # Sort by year (extract year from file path)
    glob_netcdfs.sort(key=lambda path: int(path.split('/')[-1].split('.')[1][1:]))
    year = get_ongoing_year_from_netcdf_path(glob_netcdfs[-1]) + 1
    # Generate a timepoint file to accompany the new ongoing NetCDF
    make_timepoint_xml_file(year)
    return dir_years_ndvi_netcdf + year_netcdf_filename_template.format(str(year)) + '.nc'


# Expects the first 8 characters of the filename to be of the form YYYYMMDD
def make_date_from_path (path):
  filename = path.split('/')[-1]
  return datetime.datetime.strptime(filename[0:8], '%Y%m%d')


def is_leap_year (year):
  return calendar.isleap(int(year))


def get_existing_weekly_emodis_netcdf_dates ():
  paths = glob.glob(dir_weekly_emodis_netcdf + "*.nc")
  return map(make_date_from_path, paths)


def get_full_year_emodis_dates ():
  path_ongoing_year_emodis_netcdf = get_path_to_ongoing_year_emodis_netcdf()
  filename_ongoing_year_emodis_netcdf = path_ongoing_year_emodis_netcdf.split('/')[-1]
  year = filename_ongoing_year_emodis_netcdf.split('.')[1][1:]
  path_to_emodis_dates_file = dir_years_ndvi_netcdf
  dates = []
  if is_leap_year(year):
    path_to_emodis_dates_file += 'leap-dates.txt'
  else:
    path_to_emodis_dates_file += 'nonleap-dates.txt'
  with open(path_to_emodis_dates_file, 'r') as f:
    for line in f:
      dates.append(line.strip('\n') + '-' + year)
  # Change the last date string to have the 'next' year
  last_date = dates[-1].split('-')[0:2]
  last_date.append(str(int(year)+1))
  dates[-1] = '-'.join(last_date)
  return [ datetime.datetime.strptime(date, '%m-%d-%Y') for date in dates ]


def get_emodis_tiffs_to_convert ():
  emodis_dates = get_full_year_emodis_dates()
  weekly_emodis_netcdf_dates = get_existing_weekly_emodis_netcdf_dates()

  all_weekly_emodis_tiffs = glob.glob(dir_weekly_emodis_tiffs+'*.tif')
  ongoing_year_weekly_emodis_tiffs = filter(lambda path:
    make_date_from_path(path) in emodis_dates, all_weekly_emodis_tiffs
  )
  emodis_tiffs_to_convert = filter(lambda path:
    make_date_from_path(path) not in weekly_emodis_netcdf_dates, ongoing_year_weekly_emodis_tiffs
  )
  emodis_tiffs_to_convert.sort(key=lambda path: make_date_from_path(path))
  return emodis_tiffs_to_convert


def convert_emodis_tiffs_to_netcdf (tiffs):
  for i, path in enumerate(tiffs):
    # extract the filename, removing the extension
    filename = path.split('/')[-1].split('.')[0]
    gdal_command = 'gdal_translate -of netCDF ' + path + ' ' + dir_weekly_emodis_netcdf + filename + '.nc'
    logging.debug('Convert tiff file {0} to netcdf with gdal_translate command:\n'.format(filename, gdal_command))
    os.system(gdal_command)


def get_emodis_netcdf_paths_to_concat ():
  glob_paths = glob.glob(dir_weekly_emodis_netcdf + "*.nc")
  return filter(lambda path: make_date_from_path(path) in get_full_year_emodis_dates(),
    glob_paths
  )


def sort_paths_by_filename_date (paths):
  paths.sort(key=lambda path: make_date_from_path(path))
  return paths


def concat_emodis_netcdfs_with_ongoing_file (ongoing_file, paths_to_concat):
  paths_arg = ' '.join(paths_to_concat)
  ncecat_command = 'ncecat -A {0} {1}'.format(paths_arg, get_path_to_ongoing_year_emodis_netcdf())
  logging.info('Concatenating the following files onto the ongoing year file {0}:\n{1}'.format(
    ongoing_file.split('/')[-1],
    '\n'.join(map(lambda path: path.split('/')[-1], paths_to_concat))
  ))
  logging.debug('The ncecat command to run is:\n'+ncecat_command)
  os.system(ncecat_command)


def rename_ongoing_files ():
  path_ongoing_year_netcdf = get_path_to_ongoing_year_emodis_netcdf()
  path_ongoing_year_xml = path_ongoing_year_netcdf.replace('.nc', '.ts.xml')
  os.rename(path_ongoing_year_netcdf, path_ongoing_year_netcdf.replace('ONGOING.', ''))
  os.rename(path_ongoing_year_xml, path_ongoing_year_xml.replace('ONGOING.', ''))
  logging.info('Ongoing netcdf file {0} is complete. Renaming to remove "ONGOING" from filename'.format(
    path_ongoing_year_netcdf.split('/')[-1]
  ))


def remove_weekly_netcdfs ():
  paths = glob.glob('{0}*.nc'.format(dir_weekly_emodis_netcdf))
  for path in paths:
    logging.info('Remove weekly emodis file {0}'.format(path))
    os.remove(path)


def remove_old_logs ():
  four_weeks_ago = datetime.date.today() - datetime.timedelta(28)
  glob_logs = glob.glob(os.getcwd() + 'logs/*.log')
  old_log_dates = filter(lambda path:
    datetime.strptime(path.split('/')[-1].replace('.log', ''), '%Y%m%d') < four_weeks_ago, glob_logs)
  for date in old_log_dates:
    date_string = date.strftime('%Y%m%d')
    logging.info('Deleting old log file {0}.log'.format(date_string))
    os.remove('{0}logs/{1}.log'.format(os.getcwd(), date_string))


def remove_temp_files ():
  glob_files = glob.glob(dir_years_ndvi_netcdf + '*.tmp')
  for path in glob_files:
    os.remove(path)


def cleanup ():
  existing_weekly_emodis_netcdf_dates = get_existing_weekly_emodis_netcdf_dates()
  full_year_emodis_netcdf_dates = get_full_year_emodis_dates()
  if (len(existing_weekly_emodis_netcdf_dates) == len(full_year_emodis_netcdf_dates)):
    # We have a year's worth of weekly emodis netcdfs
    # Assume the ongoing year netcdf is done
    # Rename ongoing netcdf so next time a new year's file is created
    rename_ongoing_files()
    remove_weekly_netcdfs()
    remove_old_logs()
    remove_temp_files()


def setup_logging ():
  today = datetime.date.today().strftime('%Y%m%d')
  os.system('touch {0}/logs/{1}.log'.format(os.getcwd(), today))
  logging.basicConfig(filename='{0}/logs/{1}'.format(os.getcwd(), today+'.log'), level=logging.DEBUG)


def main ():
  setup_logging()
  emodis_tiffs_to_convert = get_emodis_tiffs_to_convert()
  if (len(emodis_tiffs_to_convert) > 0):
    logging.info('Converting the following tiffs to netcdf:\n' +
      '\n'.join(map(lambda path: path.split('/')[-1], emodis_tiffs_to_convert))
    )
    convert_emodis_tiffs_to_netcdf(emodis_tiffs_to_convert)
    netcdfs_to_concat = get_emodis_netcdf_paths_to_concat()
    if not ongoing_file_exists():
      ongoing_file_path = get_path_to_ongoing_year_emodis_netcdf()
      year = get_ongoing_year_from_netcdf_path(ongoing_file_path)
      make_timepoint_xml_file(year)
    if len(netcdfs_to_concat) > 0:
      netcdfs_to_concat = sort_paths_by_filename_date(netcdfs_to_concat)
      concat_emodis_netcdfs_with_ongoing_file(get_path_to_ongoing_year_emodis_netcdf(), netcdfs_to_concat)

  else:
    logging.info('Found no tiffs to convert. Assuming any tiffs already converted have been concatenated.')

  cleanup()


main()