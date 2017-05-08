## fcav-ndvi.nemac.org

This application contains the code and data needed for the server-side
part of the "multigraph" feature of NEMAC's FCAV viewer.  This is the
feature that allows a user to click on a point in the map and see a
graph of historical NDVI values for that point. The code and data
here provide a service that receives requests from the FCAV
application containing the coordinates of a point, and returns a MUGL
file containing the graph specification and data for the NDVI graph
for that point.

The resulting timeseries differentiates NDVI data from two data sources:
smoothed MODIS data and unprocessed "raw" eMODIS data. The unprocessed
data serves to provide data for the recent past when smoothed
MODIS data is unavailable. When a smoothed NetCDF file becomes available,
it should replace its unsmoothed counterpart (see "Adding a new NetCDF file").

  * `data` directory

    This directory contains the NetCDF NDVI data files.  There is
    generally one NetCDF `*.nc` file per year, along with a corresponding
    file ending in ".ts.xml" which gives the dates associated with
    the data in the file.  See below for more details.  The NetCDF `*.nc`
    files here are excluded from the project git repository, because
    they are very large (one file per year starting with 2010, each file
    is about 13GB).

    The subdirectory `emodis_weekly` has NetCDFs containing 8-day eMODIS NDVI.
    The eMODIS data files are generated on a weekly basis from tiff files and
    appended to an ongoing partial year NetCDF file located in the
    parent directory with the word "ONGOING" in the filename.
    When a partial year NetCDF is completed, "ONGOING" is removed from
    the filename automatically. Partial and full year eMODIS NetCDFs
    in the `data` directory are distinguished by the presence of the word
    "RAW" in the filename. 
    
  * `html` directory: this is the web root of the project, containing
    a single python script `tsmugl_product.cgi` that implements the service

  * `Config.py`: configuration file used by the script above; this file
    contains the location of the `data` directory, and a list of the
    data files to be used.
      
  * `mugl.tpl.xml`: template file used by the above script when generating
    the MUGL graph file

## NetCDF File Structure

The `tsmugl_product.cgi` script expects the data in the NetCDF files
to adhere to a very specific structure; the best way to see the detals
of that structure
is to run the command `ncdump -h` on one of the existing files; a sample
output from that command is contained in the file `NetCDF-Format.md`.

In general, the file must contain three dimensions: `x` and `y` dimensions
corresponding to spatial map coordinates, and a dimension called `record`
that corresponds to time.  This `record` dimension is defined as an
"unlimited" dimension in the file, and contains one value per date
for the data in the file.  Typically each of these NetCDF files contains
the data for one year, which comes to 46 dates throughout 
the year, each separated from the next by 8 days. The NetCDF files does
not contain the actual dates themselves -- the `record`
dimension simply serves as an index for the sequence of dates.  The
dates themselves are stored in a separate file which ends with the
suffix `*.ts.xml`.

When NEMAC receives a new NetCDF file to be deployed here, we only
receive the `*.nc` file; we have to create the corresponding `*.ts.xml`
file by hand and add it to the `data` directory along with the `*.nc`
file.

## Adding New NDVI Data Files

To add a new data file:

1. Put the new NetCDF `*.nc` file in the `data` directory

2. Create a file containing the dates corresponding to the data in
   the new `*.nc` file; this file should have the same name as the `*.nc`
   file, but should end with the suffix ".ts.xml" rather than ".nc".
   This file should be in the data directory along with the `*.nc` file.
   If the NDVI data file is a smoothed MODIS file replacing an
   unprocessed eMODIS data file, there should be a dates file already.
   In this case, simply remove the word "RAW" from the filename and
   verify that the file (minus the suffix) has the same name as the
   ingoing data file.

   As mentioned above, this file contains the dates for the data
   contained in the `*.nc` file.  To see the format of this file, look
   at one of the existing `*.ts.xml` files and follow the pattern there.
   The file should contain one `<timepoint>` corresponding each date
   for which the NetCDF contains data.
   
   To create the `*.ts.xml` file for a new year's `*.nc` file, copy a
   previous year's `*.ts.xml` file and change the dates it contains to
   be correct for the new year's `*.nc` file.  This involves figuring
   out what the 46 dates for the new year should be.

   The best way to get these 46 dates is to get the exact list of them
   from the person who provided the new year's `*.nc` file -- just ask
   them to tell you what the dates are that correspond to the data.
   They might only tell you what the first date in the file is, in
   which case you can figure out the other 45 by stepping forward 8
   days at a time.
   
   If you are not able to get the exact list of dates along with the
   `*.nc` file, it's also OK to generate them by just copying the
   `*.ts.xml` file from a previous year, and changing the year(s) of the
   dates it contains to correspond to the new data.  While this isn't
   technically correct, the effect of doing this will simply be that
   the data points in the plot for this year of data will possibly be
   off by a few days in one direction or another, which is not a
   disaster.  If you do generate the new file's date list by copying a
   previous year's date list, be sure to copy a year that matches the
   "leapness" of the new data's year -- i.e. for a leap year, copy the
   `*.ts.xml` file from another leap year, and for a non-leap year, copy
   one from a non-leap year.  The files `leap-dates.txt` and
   `nonleap-dates.txt` in the `data` directory may also be used to
   generate the new date list.
   
   In any case, however you create the new year's list of dates,
   note that the last date in a `*.ts.xml` file is usually in January of
   the following year, so be careful to set the year of this date
   correctly when creating a `*.ts.xml` file.
   
   Also note that it's OK for a file to contain less than a full year
   of data; sometimes the EFETAC team gives us a half year of data
   before the full year is available.  Just make sure that you have a
   `*.ts.xml` file that contains one `<timepoint>` entry for each
   date of data present in the NetCDF file.
   
3. Edit the `Config.py` file to add the name of the new `*.nc`
   file, without the ".nc" suffix, to end of the `data_files` array.
   Make sure the the data files in this array are given in
   chronological order -- i.e. new years should be added at the end
   of the list.
   
   Also, if you are deploying a full year data file to replace a
   previously deployed partial year file, or a raw eMODIS file,
   be sure to remove the partial year from from the list in `Config.py`.

   Note: eMODIS files do not need ".RAW" or ".RAW.ONGOING" added to them
   in the config file. The paths for these files is resolved programmatically
   from the "base" filename.
   
4. Edit the `mugl.tpl.xml` file to change the `max` attribute of
   the `<horizontalaxis>` element to be the last day of the month
   of the last date for which there is data.  For example, if the
   last data data is "20140102", set `max` to "20140131".

5. Test the service by running FCAV in a browser, selecting the
   Multigraph tool, clicking on a point in the map to bring up the
   Multigraph, and check to make sure that (a) the graph appears, and
   (b) it contains the data for the new year, and (c) when the graph
   initially appears, it shows the entire time range of available data.
   
6. Commit the changes to the project git repo with an appropriate
   log message, and push to origin.
