# NetCDF Format

Below is the output of the command `ncdump -h MCD13.A2013.unaccum.nc`, showing the structure
of one of the NetCDF files.


```
netcdf MCD13.A2013.unaccum {
dimensions:
	x = 20249 ;
	y = 14276 ;
	record = UNLIMITED ; // (46 currently)
variables:
	char lambert_azimuthal_equal_area(record) ;
		lambert_azimuthal_equal_area:Northernmost_Northing = 1013959.88010402 ;
		lambert_azimuthal_equal_area:Southernmost_Northing = -2293166.29041574 ;
		lambert_azimuthal_equal_area:Easternmost_Easting = 2640421.05042961 ;
		lambert_azimuthal_equal_area:Westernmost_Easting = -2050388.54797713 ;
		lambert_azimuthal_equal_area:spatial_ref = "PROJCS[\"Lambert_Azimuthal_Equal_Area\",GEOGCS[\"GCS_sphere\",DATUM[\"unknown\",SPHEROID[\"Spherical_Earth\",6370997,\"inf\"]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]],PROJECTION[\"Lambert_Azimuthal_Equal_Area\"],PARAMETER[\"latitude_of_center\",45],PARAMETER[\"longitude_of_center\",-100],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"Meter\",1]]" ;
		lambert_azimuthal_equal_area:GeoTransform = "-2.05039e+06 231.656 0 1.01396e+06 0 -231.656 " ;
		lambert_azimuthal_equal_area:grid_mapping_name = "lambert_azimuthal_equal_area" ;
		lambert_azimuthal_equal_area:longitude_of_central_meridian = -100.f ;
		lambert_azimuthal_equal_area:false_easting = 0.f ;
		lambert_azimuthal_equal_area:false_northing = 0.f ;
	byte Band1(record, y, x) ;
		Band1:grid_mapping = "lambert_azimuthal_equal_area" ;
		Band1:long_name = "GDAL Band Number 1" ;
		Band1:COLOR_TABLE_RULE_RGB_0 = "0.000000e+00 9.700000e+01 0 0 0 255 255 255" ;
		Band1:COLOR_TABLE_RULES_COUNT = "1" ;
		Band1:LAYER_TYPE = "athematic" ;

// global attributes:
		:Conventions = "CF-1.0" ;
		:history = "Tue Oct 14 11:18:50 2014: ncecat MCD13.A2013.unaccum.1.nc MCD13.A2013.unaccum.2.nc MCD13.A2013.unaccum.3.nc MCD13.A2013.unaccum.4.nc MCD13.A2013.unaccum.5.nc MCD13.A2013.unaccum.6.nc MCD13.A2013.unaccum.7.nc MCD13.A2013.unaccum.8.nc MCD13.A2013.unaccum.9.nc MCD13.A2013.unaccum.10.nc MCD13.A2013.unaccum.11.nc MCD13.A2013.unaccum.12.nc MCD13.A2013.unaccum.13.nc MCD13.A2013.unaccum.14.nc MCD13.A2013.unaccum.15.nc MCD13.A2013.unaccum.16.nc MCD13.A2013.unaccum.17.nc MCD13.A2013.unaccum.18.nc MCD13.A2013.unaccum.19.nc MCD13.A2013.unaccum.20.nc MCD13.A2013.unaccum.21.nc MCD13.A2013.unaccum.22.nc MCD13.A2013.unaccum.23.nc MCD13.A2013.unaccum.24.nc MCD13.A2013.unaccum.25.nc MCD13.A2013.unaccum.26.nc MCD13.A2013.unaccum.27.nc MCD13.A2013.unaccum.28.nc MCD13.A2013.unaccum.29.nc MCD13.A2013.unaccum.30.nc MCD13.A2013.unaccum.31.nc MCD13.A2013.unaccum.32.nc MCD13.A2013.unaccum.33.nc MCD13.A2013.unaccum.34.nc MCD13.A2013.unaccum.35.nc MCD13.A2013.unaccum.36.nc MCD13.A2013.unaccum.37.nc MCD13.A2013.unaccum.38.nc MCD13.A2013.unaccum.39.nc MCD13.A2013.unaccum.40.nc MCD13.A2013.unaccum.41.nc MCD13.A2013.unaccum.42.nc MCD13.A2013.unaccum.43.nc MCD13.A2013.unaccum.44.nc MCD13.A2013.unaccum.45.nc MCD13.A2013.unaccum.46.nc MCD13.A2013.unaccum.thirdtry.nc" ;
		:nco_openmp_thread_number = 1 ;
}
```
