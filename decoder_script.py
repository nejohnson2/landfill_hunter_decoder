import urllib2
import os
import zipfile
import pandas as pd
import json
import ast

def retrieveData():
	url = 'http://crowdcrafting.org/project/landfill/tasks/export?type=task_run&format=csv'
	response = urllib2.urlopen(url)
	output = open('landfill_data.zip', 'wb')
	output.write(response.read())
	output.close()    
	return unzip()

def unzip():
    fh = open('landfill_data.zip', 'rb')
    z = zipfile.ZipFile(fh)
    for name in z.namelist():
        outpath = ""
        z.extract(name, outpath)
    fh.close()
    os.remove('landfill_data.zip')
    
    return load_data(name)
    
def load_data(fileName):
    print "Reading Data..."
    data = pd.read_csv(fileName, error_bad_lines=False)
    return data        

def create_feature(record):
    if record != '0':
        record = ast.literal_eval(record)
        for i in record:
            geometry = ast.literal_eval(i['area_geometry'])
            properties = i['area']
            obj_id = i['id']
            result = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {"area" : properties, "id" : obj_id}
            }

            return result

def create_geojson(data):
    features = list(filter(None, map(create_feature, data)))
    return json.dumps({
        "type": "FeatureCollection",
        "features": features,
    })

def writeFile(geojson):
	outputFile = open('landfill_geojson.geojson', 'wb')
	outputFile.write(geojson)
	outputFile.close()

if __name__ == '__main__':
	data = retrieveData()
	geojson = create_geojson(data['task_runinfo__area'][0:10])
	writeFile(geojson)