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

def create_feature(data):
    '''extract individual landfill features
    with their associated properties'''

    record = data[0]
    if record != '0':
        record = ast.literal_eval(record)
        
        # loop through records if there are multiple
        for i in record:
            geometry = ast.literal_eval(i['area_geometry'])
            result = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "area" : i['area'], 
                    "id" : i['id'], 
                    "fac_name" : data[1],
                    "fac_state" : data[2],
                    "fac_street" : data[3],
                    "task_id" : data[4],
                    "task_user_id" : data[5],
                    "task_runinfo__skip" : data[6],
                }
            }
    else:
        result = {
            "type": "Feature",
            "geometry": None,
            "properties": {
                "area" : 0,
                "id" : None,
                "fac_name" : data[1],
                "fac_state" : data[2],
                "fac_street" : data[3],
                "task_id" : data[4],
                "task_user_id" : data[5],
                "task_runinfo__skip" : data[6],
            }
        }
    
    return result            

def create_geojson(data):
    '''collect features to make geojson'''
    # this is a hack to map data columns to the 
    # create_feature function.
    temp = zip(
                list(data['task_runinfo__area']),
                list(data['task_runinfo__Facility_Name']),
                list(data['task_runinfo__Facility_State']),
                list(data['task_runinfo__Facility_Street']),
                list(data['task_run__task_id']),
                list(data['task_run__user_id']),
                list(data['task_runinfo__skip']),    
              )

    features = list(map(create_feature, temp))
    
    return json.dumps({
        "type": "FeatureCollection",
        "features": features,
    })    

def writeFile(geojson):
	print "Writing geojson file..."
	outputFile = open('landfill_geojson.geojson', 'wb')
	outputFile.write(geojson)
	outputFile.close()

if __name__ == '__main__':
	data = retrieveData()
	geojson = create_geojson(data)
	writeFile(geojson)
	print "Finished"