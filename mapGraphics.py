import pygame, sys, random, time, csv, ast, requests, math, pickle
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
from copy import copy

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

    lim_coord = [45.41960958653527, 12.29609707081636, 45.46473083343668, 12.368291065858616]
    lim_width = lim_coord[3]-lim_coord[1]
    lim_height = lim_coord[2]-lim_coord[0]
    map_centre = [lim_width/2 + lim_coord[1],
                    lim_height/2 + lim_coord[0]]

    scaling = min(screen_width/lim_width, screen_height/lim_height)
    monthRange = [0,12]
    yearRange = [2003, 2020]

    # Variables to keep track of the scenes
    cycle = 0
    frame = 0
    step = 2000
    RedrawBackground = True
    Wait = False
    Buildup = False
    ShowData = False
    Recommend = False
    ShowInfo = False
    shownUsers = []
    shownPhotos = []
    chosenPhotos = []
    baseScreen = None

    minlat = 45.327555
    minlon = 12.198333
    cellSize = 0.0001
    nrCellsX = 3934
    nrCellsY = 1371

    # Initiate Graphics class with the pygame screen, and loading the photos, users and grid
    def __init__(self):
        self._screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.photo_surface = pygame.surface.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)
        self.connection_surface = pygame.surface.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)
        self.cursor_surface = pygame.surface.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)

        with open ("picsSorted.p", 'rb') as fp:
            self.photos = pickle.load(fp)
        with open ("userDict.p", 'rb') as fp:
            self.users = pickle.load(fp)
        with open ("photoGrid.p", 'rb') as fp:
            self.grid = pickle.load(fp)

    def draw_screen(self, screen):
        pygame.init()
        pygame.display.set_caption('flick map 1')

    def map_coordinate(self, latlon):
        y = self.screen_centre[1] - ((float(latlon[0]) - self.map_centre[1]) * self.scaling)
        x = self.screen_centre[0] + ((float(latlon[1]) - self.map_centre[0]) * self.scaling)
        return[int(x),int(y)]

    def inv_coordinates(self, point):
        lon = (point[0] - self.screen_centre[0])/self.scaling + self.map_centre[0]
        lat = -(point[1] - self.screen_centre[1])/self.scaling + self.map_centre[1]
        return (lat, lon)

    def getGridCell(self):
        mouseP = pygame.mouse.get_pos()
        (lat, lon) = self.inv_coordinates(mouseP)
        y = lat - self.minlat
        x = lon - self.minlon
        xc = int(x/self.cellSize)
        yc = int(y/self.cellSize)
        if (xc < self.nrCellsX and yc < self.nrCellsY) and (xc > 0 and yc > 0):
            return(self.grid[xc][yc])

    def draw_photo(self, photo, radius, shape, c = None):
        centre = self.map_coordinate([photo[0][0], photo[0][1]])
        if photo[4]:
            if c:
                color = c
            else:
                color = tuple(hex(photo[4]).rgb)
            r = radius
            if shape == "circle":
                pygame.draw.circle(self.photo_surface, color, centre, r)
            if shape == "cross":
                pygame.draw.line(self.connection_surface, color, (centre[0]-r, centre[1]), (centre[0]+r, centre[1]), int(r/2))
                pygame.draw.line(self.connection_surface, color, (centre[0], centre[1]-r), (centre[0], centre[1]+r), int(r/2))

    def getUserColor(self, user):
        c = ColorHash(user)
        return(c.rgb)

    def draw_connection(self, c1, c2, colour):
        p1 = self.map_coordinate(c1)
        p2 = self.map_coordinate(c2)
        pygame.draw.line(self.connection_surface, colour, p1, p2, 1)

    def showPhoto(self, p):
        imageUrl = p[3]
        try:
            imageStr = urlopen(imageUrl).read()
            im = BytesIO(imageStr)
            #im = im.resize((150,150))
            photo = pygame.image.load(im)
            rect = photo.get_rect()
            pLoc = self.map_coordinate(p[0])
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.bottomleft, 1)
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.topright, 1)
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.bottomright, 1)
            self.connection_surface.blit(photo, [0,0])
        except OSError:
            return None

    def showLocation(self, latlon):
        locator = Nominatim(user_agent="myGeocoder")
        try:
            location = str(locator.reverse(latlon))
            locationText = myfont.render(location.partition(",")[0], False, (255,255,255))
            self.connection_surface.blit(locationText, (50, self.screen_height - 50))
        except:
            pass

    def drawSelectedPhotos(self, photos):
        showingPhoto = None
        chosenPhoto = None
        connected = []
        for p in photos:
            date = datetime.fromtimestamp(int(p[2]))
            if ((self.yearRange[0] <= date.year <= self.yearRange[1]) and
                (self.monthRange[0] <= date.month <= self.monthRange[1])):
                radius = 2 * self.ps
                centre = self.map_coordinate([p[0][0], p[0][1]])
                centre[0] -= 1
                centre[1] -= 1
                photoRect = pygame.Rect(centre, (radius,radius))
                if photoRect.collidepoint(pygame.mouse.get_pos()):
                    self.draw_photo(p, self.ps * 7, "cross")
                    connected.extend(self.users[p[1]])
                    pressedL = pygame.mouse.get_pressed()[0]
                    pressedR = pygame.mouse.get_pressed()[2]
                    if pressedL:
                        showingPhoto = p
                    if pressedR:
                        if p not in chosenPhotos:
                            chosenPhoto = p

        if chosenPhoto:
            chosenPhotos.append(chosenPhoto)
        if showingPhoto:
            self.showPhoto(showingPhoto)
            self.showLocation(str(showingPhoto[0][1]) + ", " + str(showingPhoto[0][0]))

        if len(connected) > 1:
            for i in range(len(connected)-1):
                colour = self.getUserColor(connected[i][1])
                self.draw_connection(connected[i][0], connected[i+1][0], colour)
                self.draw_photo(connected[i], self.ps * 50, "cross")
            self.draw_photo(connected[i+1], self.ps * 5, "cross")


    def drawMouse(self):
        mouseP = pygame.mouse.get_pos()
        pygame.draw.line(self.cursor_surface, (100,100,100), (mouseP[0], 0), (mouseP[0], self.screen_height), 1)
        pygame.draw.line(self.cursor_surface, (100,100,100), (0, mouseP[1]), (self.screen_width, mouseP[1]), 1)
        lat, lon = self.inv_coordinates(mouseP)
        latText = myfontS.render(str(lat), False, (255,255,255))
        lonText = myfontS.render(str(lon), False, (255,255,255))
        latWidth = latText.get_size()[0]
        self.cursor_surface.blit(latText, (self.screen_width - latWidth - self.buffer, mouseP[1] + self.buffer))
        self.cursor_surface.blit(lonText, (mouseP[0] + self.buffer, self.buffer))

    def move(self, dir, step):
        sH = step * self.lim_height
        sW = step * self.lim_width
        vH = dir[1] * sH
        vW = dir[0] * sW
        self.lim_coord = [self.lim_coord[0] + vW, self.lim_coord[1] + vH,
                        self.lim_coord[2] + vW, self.lim_coord[3] + vH]
        self.lim_width = self.lim_coord[2]-self.lim_coord[0]
        self.lim_height = self.lim_coord[3]-self.lim_coord[1]
        self.map_centre = [(self.lim_coord[2]-self.lim_coord[0])/2 + self.lim_coord[0],
                        (self.lim_coord[3]-self.lim_coord[1])/2 + self.lim_coord[1]]

        self.scaling = min(self.screen_width/self.lim_width, self.screen_height/self.lim_height)

    def zoom(self, arg):
        ratio = self.screen_width/self.screen_height
        pos = pygame.mouse.get_pos()
        rate = 1/20
        sW = self.lim_width * rate
        sH = self.lim_height * rate
        if arg == "in":
            self.lim_coord = [self.lim_coord[0] + sW, self.lim_coord[1] + sH,
                            self.lim_coord[2] - sW, self.lim_coord[3] - sH]
        if arg == "out":
            self.lim_coord = [self.lim_coord[0] - sW, self.lim_coord[1] - sH,
                            self.lim_coord[2] + sW, self.lim_coord[3] + sH]

        self.lim_width = self.lim_coord[2]-self.lim_coord[0]
        self.lim_height = self.lim_coord[3]-self.lim_coord[1]
        self.map_centre = [(self.lim_coord[2]-self.lim_coord[0])/2 + self.lim_coord[0],
                        (self.lim_coord[3]-self.lim_coord[1])/2 + self.lim_coord[1]]

        self.scaling = min(self.screen_width/self.lim_width, self.screen_height/self.lim_height)

        vr = ((pos[0] - self.screen_width / 2 )/ (self.screen_width/2), (self.screen_height /2 - pos [1])/(self.screen_height /2))
        self.move(vr, rate/2)

    def checkZoom(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.zoom("out")
                    #self.move((1,0), 1/15)
                if event.button == 5:
                    self.zoom("in")
                    #self.move((-1,0), 1/15)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move((-1,0), 1/15)
                if event.key == pygame.K_RIGHT:
                    self.move((1,0), 1/15)
                if event.key == pygame.K_UP:
                    self.move((0,1), 1/15)
                if event.key == pygame.K_DOWN:
                    self.move((0,-1), 1/15)

    # Draw the wait screen
    def waitScreen(self):
        waitText = myfontL.render("VENICE IN FLICKR", False, (255,255,255))
        tw, th = waitText.get_size()
        w, h = (tw + 3 * self.buffer, th + 3 * self.buffer)
        waitBox = pygame.Rect((self.screen_centre[0] - int(w/2), self.screen_centre[1] - int(h/2)),
        (w, h))
        pygame.draw.rect(self._screen, [255,255,255],
                        waitBox, 3* self.ps - 1)
        self._screen.blit(waitText, (self.screen_centre[0] - int(tw/2), self.screen_centre[1] - int(th/2)))
        if waitBox.collidepoint(pygame.mouse.get_pos()):
            self._screen.fill(pygame.Color('black'))
            self.Wait = False

    def buildupScene(self):
        for i in range(self.frame * self.step, min(self.frame * self.step + self.step, len(self.photos))):
            self.draw_photo(self.photos[i], self.ps, "circle")
        self._screen.blit(self.photo_surface, [0,0])

        date = datetime.fromtimestamp(int(self.photos[i][2]))
        gregDate = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
        dateText = myfont.render(gregDate, False, (255,255,255))
        pygame.draw.rect(self._screen, [0,0,0],
                        pygame.Rect((50, self.screen_height - 50), (200, 50)))
        self._screen.blit(dateText, (50, self.screen_height - 50))
        self.frame += 1
        if self.frame * self.step >= len(self.photos):
            self.Buildup = False

    def dataScreen(self):
        self._screen.fill(pygame.Color('black'))
        photoText = myfontL.render("PHOTOS: " +str(len(self.photos)), False, (255,255,255))
        userText = myfontL.render( "USERS :  " +  str(len(self.users)), False, (255,255,255))
        ptw, pth = photoText.get_size()
        utw, uth = photoText.get_size()

        self._screen.blit(photoText, (self.screen_centre[0] - int(ptw/2), self.screen_centre[1] - int(pth/2) - 2*self.buffer))
        self._screen.blit(userText, (self.screen_centre[0] - int(ptw/2), self.screen_centre[1] - int(pth/2) + 2*self.buffer))

    def recommendScreen(self):
        pass

    def exploreScene(self):
        #self.checkZoom()
        self.cursor_surface.fill((0,0,0,0))
        self.connection_surface.fill((0,0,0,0))

        if self.RedrawBackground:
            self.photo_surface.fill(pygame.Color('black'))
            for p in self.photos:
                self.draw_photo(p, self.ps, "circle")
            self.RedrawBackground = False

        cellPhotos = self.getGridCell()
        if cellPhotos:
            self.drawSelectedPhotos(cellPhotos)

        self.drawMouse()

        self._screen.blit(self.photo_surface, [0,0])
        self._screen.blit(self.connection_surface, [0,0])
        self._screen.blit(self.cursor_surface, [0,0])


    # Display the graphics
    def display(self):
        # Setup pygame screen
        clock = pygame.time.Clock()
        self._screen.fill(pygame.Color('black'))
        self.draw_screen(self._screen)
        pygame.display.update()

        # Animation loop
        while True:
            for event in pygame.event.get():
                # Check exit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    # Switches to control the scenes
                    # B stops the Buildup
                    if event.key == pygame.K_b:
                        if self.Buildup:
                            self.Buildup = False
                        else:
                            self.Buildup = True
                    # D shows the data overlay
                    if event.key == pygame.K_d:
                        if self.ShowData:
                            self.ShowData = False
                        else:
                            self.ShowData = True
                    # Return shows the recommended spaces
                    if event.key == pygame.K_RETURN and chosenPhotos:
                        if self.Recommend:
                            self.Recommend = False
                        else:
                            self.Recommend = True
                    # R restarts the timeline animation
                    if event.key == pygame.K_r:
                        self.buildup = True
                        self.frame = 0
                        self.wait = True
                        self._screen.fill(pygame.Color('black'))

                    if event.key == pygame.K_BACKSPACE:
                            if self.chosenPhotos:
                                self.chosenPhotos.remove(self.chosenPhotos[-1])

            # Check for the wait screen
            if self.Wait:
                self.waitScreen()

            elif self.Buildup:
                self.buildupScene()

            elif self.ShowData:
                self.dataScreen()

            elif self.Recommend:
                self.recommendScreen()

            else:
                self.exploreScene()

            pygame.display.update()
            clock.tick()
