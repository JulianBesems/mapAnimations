import csv
from logic import Dict

def clean(fileName, newFileName):
    prevOwner = ''
    prevLat = ''
    prevLon = ''
    csv_columns=['id','owner','secret','server','farm','title','ispublic',
    'isfriend','isfamily','description','dateupload','datetaken','datetakengranularity',
    'datetakenunknown','ownername','latitude','longitude','accuracy','context','place_id',
    'woeid','geo_is_family','geo_is_friend','geo_is_contact','geo_is_public',
    'url_c','height_c','width_c']
    with open(fileName) as csvfile:
        reader = csv.DictReader(csvfile)
        with open(newFileName, 'w') as newcsvfile:
            writer = csv.DictWriter(newcsvfile, fieldnames = reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if ((not ((row['owner'] == prevOwner)
                and (row['latitude'] == prevLat)
                and (row['longitude'] == prevLon)))
                and (float(row['latitude']) > 45.3270510147
                and float(row['longitude']) > 12.1962566155
                and float(row['latitude']) < 45.46473083343668
                and float(row['longitude']) < 45.5775260091)):
                    prevOwner = row['owner']
                    prevLat = row['latitude']
                    prevLon = row['longitude']
                    writer.writerow(row)

#clean('VeniceKWComplete.csv', 'VeniceCleanedComplete.csv')
Dict('VeniceCleanedComplete.csv')
