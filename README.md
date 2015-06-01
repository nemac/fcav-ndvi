## fcav-ndvi.nemac.org

This application contains the code and data needed for the server-side
part of the "multigraph" feature of NEMAC's FCAV viewer.  This is the
feature that allows a user to click on a point in the map and see a
graph of historical NDVI values for that point.  The code and data
here provides a service that receives requests from FCAV containing
the coordinates of a point, and returns a MUGL file containing the
graph specification and data for the NDVI graph for that point.

  * `data` directory

    This directory contains the NetCDF NDVI data files.  There is
    generally one NetCDF (*.nc) file per year, along with a corresponding
    file ending in ".ts.xml" which gives the dates associated with
    the data in the file.  See below for more details.  The NetCDF (*.nc)
    files here are excluded from the project git repository, because
    they are very large (one file per year starting with 2010, each file
    is about 13GB).

    
  * `html` directory: this is the web root of the project, containing
    a single python script `tsmugl_product.cgi` that implements the service

  * `Config.py`: configuration file used by the script above; this file
    contains the location of the `data` directory, and a list of the
    data files to be used.
      
  * `mugl.tpl.xml`: template file used by the above script when generating
    the MUGL graph file

## NetCDF File Structure

The tsmugl_product.cgi script expects the data in the NetCDF files
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
suffix *.ts.xml.

When NEMAC receives a new NetCDF file to be deployed here, we only
receive the *.nc file; we have to create the corresponding *.ts.xml
file by hand and add it to the `data` directory along with the *.nc
file.

## Adding New NDVI Data Files

To add a new data file:

1. Put the new NetCDF *.nc file in the `data` directory

2. Create a file containing the dates corresponding to the data in
   the new *.nc file; this file should have the same name as the *.nc
   file, but should end with the suffix ".ts.xml" rather than ".nc".
   This file should be in the data directory along with the *.nc file.

   As mentioned above, this file contains the dates for the data
   contained in the *.nc file.  To see the format of this file, look
   at one of the existing *.ts.xml files and follow the pattern there.
   The file should contain one `<timepoint>` these give the dates
   corresponding to the data present in the NetCDF file.
   
   To create the *.ts.xml file for a new year's *.nc file, copy a
   previous year's *.ts.xml file and change the dates it contains to
   be correct for the new year's *.nc file.  This involves figuring
   out what the 46 dates for the new year should be.

   The best way to get these 46 dates is to get the exact list of them
   from the person who provided the new year's *.nc file -- just ask
   them to tell you what the dates are that correspond to the data.
   They might only be able to tell you what the first date is, in
   which case you can figure out the other 45 by stepping forward 8
   days at a time.
   
   If you are not able to get the exact list of dates along with the
   *.nc file, it's also OK to generate them by just copying the
   *.ts.xml file from a previous year, and changing the year(s) of the
   dates it contains to correspond to the new data.  While this isn't
   technically correct, the effect of doing this will simply be that
   the data points in the plot for this year of data will possibly be
   off by a few days in one direction or another, which is not a
   disaster.  If you do generate the new file's date list by copying a
   previous year's date list, be sure to copy a year that matches the
   "leapness" of the new data's year -- i.e. for a leap year, copy the
   *.ts.xml file from another leap year, and for a non-leap year, copy
   one from a non-leap year.  The files `leap-dates.txt` and
   `nonleap-dates.txt` in the `data` directory may also be used to
   generate the new date list.
   
   Note that the last date in a *.ts.xml file is often in January of
   the following year, so be careful to set the year of this date
   correctly when creating a *.ts.xml file.
   
   partial!
   
3. Edit the `Config.py` file to add the name of the new *.nc
   file, without the ".nc" suffix, to end of the `data_files` array.
   
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
