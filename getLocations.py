from geopy.geocoders import Nominatim
from urllib.request import urlopen
import csv

screen_width = 3360 #3360 #1920 #1440 #2560 #1500 #1400 #2000 #1440
screen_height = 2100 #2100 #1080 #823 #1600 #1000 #800 #1143 #823
screen_centre = [screen_width/2, screen_height/2]

lim_coord = [12.291284137813543, 45.41960958653527, 12.372472707313529, 45.46473083343668]
lim_width = lim_coord[2]-lim_coord[0]
lim_height = lim_coord[3]-lim_coord[1]
map_centre = [(lim_coord[2]-lim_coord[0])/2 + lim_coord[0],
                (lim_coord[3]-lim_coord[1])/2 + lim_coord[1]]

scaling = min(screen_width/lim_width, screen_height/lim_height)

def inv_coordinates(point):
    lat = (point[0] - screen_centre[0])/scaling + map_centre[0]
    lon = (point[1] - screen_centre[1])/scaling + map_centre[1]
    return (lon, lat)


def getLocation(latlon):
    locator = Nominatim(user_agent="myGeocoder")
    try:
        location = str(locator.reverse(latlon))
    except:
        location = None
    print(location)
    return(location)

with open("locationsPixels.csv", 'w') as newcsvfile:
    writer = csv.writer(newcsvfile)
    for i in range(screen_width):
        print(str(i) + "/" + str(screen_width))
        for j in range(screen_height):
            latlon = inv_coordinates((i,j))
            loc = getLocation(latlon)
            writer.writerow([i,j,loc])
