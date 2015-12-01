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

def create_features(data):
    output = []
    record = ast.literal_eval(data[0])

    for i in record:
        geometry = ast.literal_eval(i['area_geometry'])
        for point in geometry['coordinates']:
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
                    "task_runinfo__certain" : data[7],
                    "task_run__user_ip" : data[8],
                    "task_run__id" : data[9],
                    "task_run__created" : data[10],
                    "task_run__finish_time" : data[11],
                }
            }
            output.append(result)
            
    return output                                                         

def create_geojson(data):
    #a stupid hack - zip all of these lists and pass them
    # into the create_feature function as variable temp
    
    data = data[data['task_runinfo__area'] != '0']
    
    temp = zip(
                list(data['task_runinfo__area']),
                list(data['task_runinfo__Facility_Name']),
                list(data['task_runinfo__Facility_State']),
                list(data['task_runinfo__Facility_Street']),
                list(data['task_run__task_id']),
                list(data['task_run__user_id']),
                list(data['task_runinfo__skip']),
                list(data['task_runinfo__certain']),
                list(data['task_run__user_ip']),
                list(data['task_run__id']),
                list(data['task_run__created']),
                list(data['task_run__finish_time']),
              )

    features = map(create_features, temp)

    # flatten the list
    features = [item for sublist in features for item in sublist]

    # remove entries without a geometry - no geometry causes import to fail
    for index,feature in enumerate(features):
        if len(feature['geometry']['coordinates'][0]) < 3:
            del features[index]
        if feature['properties']['area'] == 0:
            del features[index]

    geojson = json.dumps({
        "type": "FeatureCollection",
        "features": features,
    })
    
    return geojson

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