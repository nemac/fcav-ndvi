## FCAV2 NDVI Multigraph Service

This application contains the code and data needed for the server-side
part of the "multigraph" feature of NEMAC's FCAV2 viewer. This is the
feature that allows a user to click on a point in the map and see a
graph of historical NDVI values for that point. The code and data
here provide a service that receives requests from the FCAV2
application containing the coordinates of a point, and returns a MUGL
file containing the graph specification and data for the NDVI graph
for that point.

The resulting timeseries differentiates NDVI data from two data sources:
Standard and Near-Realtime.

  * `data` directory

    Directory of symlinks to data sources on disk.
    
  * `html` directory: this is the web root of the project, containing
    a single python script `tsmugl_product.cgi` that implements the service

  * `config.py`: configuration file used by the script above; this file
    contains the location of the `data` directory, and a list of the
    data files to be used.
      
  * `mugl.tpl.xml`: template file used by the above script when generating
    the MUGL graph file


## All-year STD Maxes TIF File Structure

Typically each of these files contains
the data for one year, which comes to 46 bands throughout 
the year, each separated from the next by 8 days. The files do
not contain the actual dates themselves.

The TIF for the current year will usually have less than 46 bands
and is actively rebuilt as part of the ForWarn 2 production process.


## NRT maxes

Any available NRT data for dates where STD is not available yet
is appended to the retrieved STD data and colored red in the viewer.


