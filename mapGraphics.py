import pygame, sys, random, time, csv, ast, requests, math
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
from logic import SmallDict
import numpy as np
from colors import rgb, hex
from geopy.geocoders import Nominatim
from datetime import datetime
from colorhash import ColorHash
from shapely import geometry
from classifyPlaces import *

pygame.font.init()
myfont = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 22)
myfontI = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 35)
myfontL = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 50)
myfontS = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 14)

infoText = ["Through the use of recommender systems digital media platforms such as Spotify present each",
           "user with a different customised experience. How the platform is perceived is informed by the",
           "behaviour of others, and the resulting relations between them. Because of this the way in which",
           "we consume media has fundamentally changed, not only from a physical platform to the digital",
           "one, but also in the choices that we make.",
           "This mapping exercise of Flickr posts in Venice is aimed at experimenting with the implementation",
           "of a recommender system in a spatial context. The next step will be to develop a process to",
           "generate spatial configurations, where each outcome is defined by how one specific input",
           "relates to the wider context that informs the recommender system."]

class Graphics:
    screen_width = 3360 #3360 #1920 #1440 #2560 #1500 #1400 #2000 #1440
    screen_height = 2100 #2100 #1080 #823 #1600 #1000 #800 #1143 #823
    screen_centre = [screen_width/2, screen_height/2]
    buffer = int(screen_height/100)
    ps = int(buffer/10)

    lim_coord = [12.29609707081636, 45.41960958653527, 12.368291065858616, 45.46473083343668]
    lim_width = lim_coord[2]-lim_coord[0]
    lim_height = lim_coord[3]-lim_coord[1]
    map_centre = [lim_width/2 + lim_coord[0],
                    lim_height/2 + lim_coord[1]]

    scaling = min(screen_width/lim_width, screen_height/lim_height)
    monthRange = [0,12]
    yearRange = [2003, 2019]

    picFile = "imagesCColourA.csv"

    def __init__(self):
        self._screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.photos = []
        with open(self.picFile) as csvfile:
            reader = csv.reader(csvfile)
            for r in reader:
                r[0] = ast.literal_eval(r[0])
                if r[4]:
                    self.photos.append(r)

        self.photos.sort(key = lambda x : x[2])
