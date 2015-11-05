# Landfill Hunter Decoder

This is a project to analyze the data being generated from the Landfill Hunter project running on Crowdcrafting [here](http://crowdcrafting.org/project/landfill/).  The script downloads the csv file from crowdcrafting and parses the data into a geojson file.  

The geojson file is then converted to a shapefile by using:

```
ogr2ogr -f "ESRI Shapefile" landfills.shp "landfill_geojson.geojson"
```