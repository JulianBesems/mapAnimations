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
from classifyPlaces2 import LocationGrid, Cell, Group, LocationGroups
from recommenderGraph import CooccurenceMatrix

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
    Wait = True
    Buildup = True
    ShowData = False
    Recommend = False
    RecommendOld = False
    ShowInfo = False
    LocationGridShow = False
    showGrid = True
    shownUsers = []
    previousPhotoUrl = None
    previousPhoto = None
    shownPhotos = []
    chosenPhotos = []
    baseScreen = None
    flipMatrix = False
    expNr = 2

    connected = []

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
        #with open ("preprocessedPhotos.p", 'rb') as fp:
        #    self.photos = pickle.load(fp)
        with open ("userDict.p", 'rb') as fp:
            self.users = pickle.load(fp)
        with open ("photoGrid.p", 'rb') as fp:
            self.grid = pickle.load(fp)
        with open ("ccMatrixDirProp2.p", 'rb') as fp:
            self.ccMatrix = pickle.load(fp)

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

    def draw_photo(self, photo, radius, shape, c = None, surface = None):
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

    def draw_connection(self, c1, c2, colour, w = None):
        p1 = self.map_coordinate(c1)
        p2 = self.map_coordinate(c2)
        if w:
            pygame.draw.line(self.connection_surface, colour, p1, p2, w)
        else:
            pygame.draw.line(self.connection_surface, colour, p1, p2, 1)

    def showPhoto(self, p):
        imageUrl = p[3]
        try:
            if imageUrl == self.previousPhotoUrl:
                photo = self.previousPhoto
            else:
                imageStr = urlopen(imageUrl).read()
                im = BytesIO(imageStr)
                #im = im.resize((150,150))
                photo = pygame.image.load(im)
            rect = photo.get_rect()
            pLoc = self.map_coordinate(p[0])
            print(p[3])
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.bottomleft, 1)
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.topright, 1)
            pygame.draw.line(self.connection_surface, tuple(hex(p[4]).rgb), pLoc,
            rect.bottomright, 1)
            self.connection_surface.blit(photo, [0,0])
            self.previousPhotoUrl = imageUrl
            self.previousPhoto = photo
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
        self.connected = []
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
                    self.connected.extend(self.users[p[1]])
                    pressedL = pygame.mouse.get_pressed()[0]
                    pressedR = pygame.mouse.get_pressed()[2]
                    pressedM = pygame.mouse.get_pressed()[1]
                    if pressedL:
                        showingPhoto = p
                    if pressedR:
                        if p not in self.chosenPhotos:
                            chosenPhoto = p
                    if pressedM:
                        photos = self.users[p[1]]
                        self.chosenPhotos = photos

        if chosenPhoto:
            self.chosenPhotos.append(chosenPhoto)

        if showingPhoto:
            self.showPhoto(showingPhoto)
            self.showLocation(str(showingPhoto[0][0]) + ", " + str(showingPhoto[0][1]))

        if len(self.connected) > 1:
            for i in range(len(self.connected)-1):
                colour = self.getUserColor(self.connected[i][1])
                self.draw_connection(self.connected[i][0], self.connected[i+1][0], colour)
                self.draw_photo(self.connected[i], self.ps * 5, "cross")
            self.draw_photo(self.connected[-1], self.ps * 5, "cross")

    def timeSlider(self):
        widthm = self.buffer * 12
        widthy = self.buffer * (2020-2003)
        startxm = self.screen_centre[0] - int(widthm/2)
        startxy = self.screen_centre[0] - int(widthy/2)
        mStep = int(widthm/12)
        yStep = int(widthy/(2020-2003))
        mouseP = pygame.mouse.get_pos()
        for i in range(12):
            box = pygame.Rect((startxm + i*mStep, self.buffer * 5 - 3 * self.ps),
                            (mStep, 6 * self.ps))
            if box.collidepoint(mouseP):
                mText = myfontS.render(str(i+1), False, (255,255,255))
                self.cursor_surface.blit(mText, (box.left + 3*self.ps, self.buffer * 5 + 4 * self.ps))
                if pygame.mouse.get_pressed()[0] and i < self.monthRange[1]:
                    self.monthRange[0] = i
                    self.RedrawBackground = True
                if pygame.mouse.get_pressed()[2] and i >= self.monthRange[0]:
                    self.monthRange[1] = i+1
                    self.RedrawBackground = True

        for i in range((2020-2003)):
            box = pygame.Rect((startxy + i*yStep, self.buffer * 3 - 3 * self.ps),
                            (yStep, 6 * self.ps))
            if box.collidepoint(mouseP):
                yText = myfontS.render(str(i+2003), False, (255,255,255))
                self.cursor_surface.blit(yText, (box.left, self.buffer * 3 + 4 * self.ps))
                if pygame.mouse.get_pressed()[0] and (i+2003) < self.yearRange[1]:
                    self.yearRange[0] = i+2003
                    self.RedrawBackground = True
                if pygame.mouse.get_pressed()[2] and (i+2003) >= self.yearRange[0]:
                    self.yearRange[1] = i+2004
                    self.RedrawBackground = True

        yRect = pygame.Rect((startxm + self.monthRange[0] * mStep, self.buffer * 5 - 3*self.ps),
                        ((self.monthRange[1]-self.monthRange[0]) * mStep, 6 * self.ps))
        mRect = pygame.Rect((startxy + (self.yearRange[0] - 2003) * yStep, self.buffer * 3 - 3*self.ps),
                        ((self.yearRange[1]-self.yearRange[0]) * yStep, 6 * self.ps))
        pygame.draw.rect(self.cursor_surface, (100,100,100), yRect)
        pygame.draw.rect(self.cursor_surface, (100,100,100), mRect)

        pygame.draw.line(self.cursor_surface, (250,250,250), (startxm, self.buffer * 5),
                        (startxm + widthm, self.buffer * 5), self.ps)
        pygame.draw.line(self.cursor_surface, (250,250,250), (startxy, self.buffer * 3),
                        (startxy + widthy, self.buffer * 3), self.ps)
        for i in range(13):
            pygame.draw.line(self.cursor_surface, (200,200,200), (startxm + i*mStep, self.buffer * 5 - 3 * self.ps),
                            (startxm + i*mStep, self.buffer * 5 + 3 * self.ps), 1)
        for j in range((2020-2003)+1):
            pygame.draw.line(self.cursor_surface, (200,200,200), (startxy + j*yStep, self.buffer * 3 - 3 * self.ps),
                            (startxy + j*yStep, self.buffer * 3 + 3 * self.ps), 1)

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

    def showInfo(self):
        iTexts = []
        for i in infoText:
            iText = myfontI.render(i, False, (255,255,255))
            iTexts.append(iText)

        tw, th = iTexts[0].get_size()
        w, h = (tw + 5 * self.buffer, len(iTexts) * (th + self.ps) + 3 * self.buffer)
        infoBox = pygame.Rect((self.screen_centre[0] - int(w/2) + self.buffer, self.screen_centre[1] - int(h/2)),
            (w, h))
        pygame.draw.rect(self._screen, [0,0,0],
                        infoBox)
        pygame.draw.rect(self._screen, [255,255,255],
                    infoBox, 3* self.ps - 1)

        for j in range(len(iTexts)):
            gap = (j  - int(len(iTexts)/2)) * (th + self.ps)
            self._screen.blit(iTexts[j], (self.screen_centre[0] - int(tw/2), self.screen_centre[1] - int(th/2) + gap))

    def move(self, dir, step):
        sH = step * self.lim_height
        sW = step * self.lim_width
        vH = dir[1] * sH
        vW = dir[0] * sW
        self.lim_coord = [self.lim_coord[0] + vH, self.lim_coord[1] + vW,
                        self.lim_coord[2] + vH, self.lim_coord[3] + vW]
        self.lim_width = self.lim_coord[3]-self.lim_coord[1]
        self.lim_height = self.lim_coord[2]-self.lim_coord[0]
        self.map_centre = [self.lim_width/2 + self.lim_coord[1],
                        self.lim_height/2 + self.lim_coord[0]]

        self.scaling = min(self.screen_width/self.lim_width, self.screen_height/self.lim_height)

    def zoom(self, arg):
        ratio = self.screen_width/self.screen_height
        pos = pygame.mouse.get_pos()
        rate = 1/20
        sW = self.lim_width * rate
        sH = self.lim_height * rate
        if arg == "in":
            self.lim_coord = [self.lim_coord[0] + sH, self.lim_coord[1] + sW,
                            self.lim_coord[2] - sH, self.lim_coord[3] - sW]
        if arg == "out":
            self.lim_coord = [self.lim_coord[0] - sH, self.lim_coord[1] - sW,
                            self.lim_coord[2] + sH, self.lim_coord[3] + sW]

        self.lim_width = self.lim_coord[3]-self.lim_coord[1]
        self.lim_height = self.lim_coord[2]-self.lim_coord[0]
        self.map_centre = [self.lim_width/2 + self.lim_coord[1],
                        self.lim_height/2 + self.lim_coord[0]]

        self.scaling = min(self.screen_width/self.lim_width, self.screen_height/self.lim_height)

        vr = ((pos[0] - self.screen_width / 2 )/ (self.screen_width/2), (self.screen_height /2 - pos [1])/(self.screen_height /2))
        self.move(vr, rate/2)

    def checkZoom(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.zoom("out")
                    self.RedrawBackground = True
                if event.button == 5:
                    self.zoom("in")
                    self.RedrawBackground = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move((-1,0), 1/15)
                    self.RedrawBackground = True
                if event.key == pygame.K_RIGHT:
                    self.move((1,0), 1/15)
                    self.RedrawBackground = True
                if event.key == pygame.K_UP:
                    self.move((0,1), 1/15)
                    self.RedrawBackground = True
                if event.key == pygame.K_DOWN:
                    self.move((0,-1), 1/15)
                    self.RedrawBackground = True


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
        self._screen.fill(pygame.Color('black'))
        self.connection_surface.fill((0,0,0,0))
        connected = []

        for p in self.chosenPhotos:
            connected.extend(self.users[p[1]])
            connected.remove(p)

        groups = []
        for a in connected:
            group = [a]
            ca = self.map_coordinate(a[0])
            for b in connected:
                cb = self.map_coordinate(b[0])
                ab = [ca[0]-cb[0], ca[1] - cb[1]]
                if math.sqrt(ab[0]**2 + ab[1]**2) < (self.buffer * 3):
                    group.append(b)
                    connected.remove(b)
            groups.append(group)

        if len(groups) > 0:
            for g in groups:
                if len(g) >= 2:
                    for i in range(len(g)-1):
                        self.draw_connection(g[i][0], g[i+1][0], (200,200,200))

            for g in groups:
                for c in g:
                    self.draw_photo(c, self.ps * 3, "cross", (200,200,200))

        if len(self.chosenPhotos) > 1:
            for i in range(len(self.chosenPhotos)-1):
                self.draw_connection(self.chosenPhotos[i][0], self.chosenPhotos[i+1][0], (200,50,50))

        for p in self.chosenPhotos:
            self.draw_photo(p, self.ps * 7, "cross", (200,50,50))

        self._screen.blit(self.connection_surface, [0,0])

    def recommendScreen2(self):
        nrRecommendations = 100

        self._screen.fill(pygame.Color('black'))
        self.connection_surface.fill((0,0,0,0))
        groups = self.ccMatrix.lcGroups

        selectedGroupIndexes = []

        for p in self.chosenPhotos:
            for g in range(len(groups)):
                if p in groups[g].photos and not g in selectedGroupIndexes:
                    selectedGroupIndexes.append(g)
                    break

        connections = []
        cGroupsIndexes = []

        for g in selectedGroupIndexes:
            for c in range(len(groups)):
                if self.ccMatrix.ccMatrix[g, c] > 0 and not g == c:
                    if not [c,0] in cGroupsIndexes:
                         cGroupsIndexes.append([c,0])
                    if self.flipMatrix:
                        connections.append([g,c, self.ccMatrix.ccMatrix[c, g]])
                    else:
                        connections.append([g,c, self.ccMatrix.ccMatrix[g, c]])

        for g in cGroupsIndexes:
            total = 0
            nr = 0
            for c in connections:
                val = (lambda x: x[2] if x[1] == g[0] else 0)(c)
                if val > 0:
                    nr += 1
                    total += val
            average = total/nr
            g[1] = average

        recGrps = []
        cGroupsIndexes.sort(key = lambda x : x[1], reverse = True)
        length = min(nrRecommendations, len(cGroupsIndexes))
        for i in range(length):
            hotness = int((i/length)*255)
            colour = (hotness, hotness, hotness)
            if self.flipMatrix:
                colour = (hotness, 0, 0)
            for l in groups[cGroupsIndexes[i][0]].locations:
                tl = self.map_coordinate([l.limits[0], l.limits[2]])
                br = self.map_coordinate([l.limits[1], l.limits[3]])
                pygame.draw.rect(self._screen, colour, [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]])
            recGrps.append((groups[cGroupsIndexes[i][0]], cGroupsIndexes[i][1]))

        selGrps = []
        for g in selectedGroupIndexes:
            colour = (150, 50, 50)
            for l in groups[g].locations:
                tl = self.map_coordinate([l.limits[0], l.limits[2]])
                br = self.map_coordinate([l.limits[1], l.limits[3]])
                pygame.draw.rect(self.connection_surface, colour, [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]])
                selGrps.append(groups[g])

        if len(self.chosenPhotos) > 1:
            for i in range(len(self.chosenPhotos)-1):
                self.draw_connection(self.chosenPhotos[i][0], self.chosenPhotos[i+1][0], (150,50,50))

        for p in self.chosenPhotos:
            self.draw_photo(p, self.ps * 7, "cross")

        self._screen.blit(self.connection_surface, [0,0])

        try:
            f = open("Recommnedation" + str(self.expNr) + "Src.csv")
            f.close()
        except IOError:
            self.exportRecommendationToRhino(selGrps, recGrps)

        if self.flipMatrix:
            self.flipMatrix = False
        else:
            pass
            #self.flipMatrix = True

    def mapCoordinatesToMetres(self, c):
        origin = (self.lim_coord[0], self.lim_coord[1])
        y = (c[0]-origin[0]) * 110574
        x = (c[1]-origin[1]) * 111320 * np.cos(np.deg2rad(c[0]))
        return(x*1000, y*1000)

    def exportRecommendationToRhino(self, src, rec):
        with open("Recommnedation" + str(self.expNr) + "Src.csv", 'w') as csvSrc:
            writer = csv.writer(csvSrc)
            for g in src:
                for l in g.locations:
                    tl = self.mapCoordinatesToMetres((l.limits[0], l.limits[2]))
                    br = self.mapCoordinatesToMetres((l.limits[1], l.limits[3]))
                    w = br[0] - tl[0]
                    h = br[1] - tl[1]
                    writer.writerow([tl[0], tl[1], w, h])

        with open("Recommnedation" + str(self.expNr) + "Rec.csv", 'w') as csvRec:
            writer = csv.writer(csvRec)
            locations = []
            for g in rec:
                v = g[1]
                for l in g[0].locations:
                    tl = self.mapCoordinatesToMetres((l.limits[0], l.limits[2]))
                    br = self.mapCoordinatesToMetres((l.limits[1], l.limits[3]))
                    w = br[0] - tl[0]
                    h = br[1] - tl[1]
                    writer.writerow([tl[0], tl[1], w, h, v])

    def exploreScene(self):
        self.cursor_surface.fill((0,0,0,0))
        self.connection_surface.fill((0,0,0,0))

        if self.RedrawBackground:
            self.photo_surface.fill(pygame.Color('black'))
            for p in self.photos:
                date = datetime.fromtimestamp(int(p[2]))
                if ((self.yearRange[0] <= date.year <= self.yearRange[1]) and
                    (self.monthRange[0] <= date.month <= self.monthRange[1])):
                    self.draw_photo(p, self.ps, "circle")
            self.RedrawBackground = False

        cellPhotos = self.getGridCell()
        if cellPhotos:
            self.drawSelectedPhotos(cellPhotos)

        if self.chosenPhotos:
            for c in self.chosenPhotos:
                self.draw_photo(c, self.ps * 7, "cross")

        self.drawMouse()
        self.timeSlider()

        self._screen.blit(self.photo_surface, [0,0])
        self._screen.blit(self.connection_surface, [0,0])
        self._screen.blit(self.cursor_surface, [0,0])

    def getLocations(self, cell, locations):
        if cell.uniform:
            locations.append(cell)
        else:
            for r in cell.subcells:
                for c in r:
                    self.getLocations(c, locations)

    def locationGridScreen(self):
        with open ("locationGrid,2,00005,07,005,nr2.p", 'rb') as fp:
            lcGrid = pickle.load(fp)
        with open ("locationGroupsWP-lin(8,00002)2.p", 'rb') as gp:
            lGroups = pickle.load(gp)
        locations = []
        self.getLocations(lcGrid.grid, locations)
        self._screen.fill(pygame.Color('black'))
        if not self.showGrid:
            for l in locations:
                tl = self.map_coordinate([l.limits[0], l.limits[2]])
                br = self.map_coordinate([l.limits[1], l.limits[3]])
                surface = ((l.limits[1]-l.limits[0]) * 100000) * ((l.limits[3]-l.limits[2]) * 100000)
                density = len(l.photos)/surface
                c = min(density * 800, 255)
                if surface > 30:
                    c2 = min(c*5, 255) #min(len(l.photos), 255)#
                    pygame.draw.rect(self._screen, [c2,c2,c2], [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]])
                    pygame.draw.rect(self._screen, [150,150,150], [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]], True)
                else:
                    pygame.draw.rect(self._screen, [0,0,0], [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]])
        else:
            maxVal = 0
            minVal = 1
            index = 0
            for g in lGroups.groups:
                if g.value > maxVal:
                    maxVal = g.value
                if g.value < minVal and not g.value == 0:
                    minVal = g.value
                #colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                colour = g.colour #tuple(hex(g.locations[0].photos[0][4]).rgb) #(random.randint(0,255), random.randint(0,255), random.randint(0,255))
                """if index == 1023:
                    colour = [255,0,0]
                    area = 0
                    first = True"""
                for l in g.locations:
                    tl = self.map_coordinate([l.limits[0], l.limits[2]])
                    br = self.map_coordinate([l.limits[1], l.limits[3]])
                    """if index == 1023 and first == True:
                        tlm = self.mapCoordinatesToMetres([l.limits[0], l.limits[2]])
                        brm = self.mapCoordinatesToMetres([l.limits[1], l.limits[3]])
                        area += abs(tlm[0] - brm[0]) * abs(tlm[1] - brm[1])
                        first = False"""
                    pygame.draw.rect(self._screen, colour, [tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]])
                """if index == 1023:
                    print(area)"""
                index +=1

    # Display the graphics
    def display(self):
        # Setup pygame screen
        clock = pygame.time.Clock()
        self._screen.fill(pygame.Color('black'))
        self.draw_screen(self._screen)
        pygame.display.update()

        # Animation loop
        while True:
            events = pygame.event.get()
            for event in events:
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
                    if event.key == pygame.K_g:
                        if self.LocationGridShow:
                            self._screen.fill(pygame.Color('black'))
                            self.RedrawBackground = True
                            self.LocationGridShow = False
                        else:
                            self.LocationGridShow = True

                    if event.key == pygame.K_SPACE:
                        if self.LocationGridShow:
                            if self.showGrid:
                                self.showGrid = False
                            else:
                                self.showGrid = True

                    # Return shows the recommended spaces
                    if event.key == pygame.K_RETURN and self.chosenPhotos:
                        if self.Recommend:
                            self._screen.fill(pygame.Color('black'))
                            self.Recommend = False
                        else:
                            self.Recommend = True
                            self.expNr += 1

                    # Return shows the old recommendation screen
                    if event.key == pygame.K_q and self.chosenPhotos:
                        if self.RecommendOld:
                            self.RecommendOld = False
                        else:
                            self.RecommendOld = True

                    # R restarts the timeline animation
                    if event.key == pygame.K_r:
                        self.Buildup = True
                        self.frame = 0
                        self.Wait = True
                        self._screen.fill(pygame.Color('black'))
                        self.photo_surface.fill(pygame.Color('black'))
                        self.RedrawBackground = True

                    if event.key == pygame.K_i:
                            if self.ShowInfo:
                                self.ShowInfo = False
                            else:
                                self.ShowInfo = True

                    if event.key == pygame.K_BACKSPACE:
                            if self.chosenPhotos:
                                if not (len(self.chosenPhotos) == 1 and self.Recommend):
                                    self.chosenPhotos.remove(self.chosenPhotos[-1])


            # Check for the wait screen
            if self.Wait:
                self.waitScreen()

            elif self.Buildup:
                self.buildupScene()

            elif self.ShowData:
                self.dataScreen()

            elif self.Recommend:
                self.recommendScreen2()

            elif self.RecommendOld:
                self.recommendScreen()

            elif self.LocationGridShow:
                self.locationGridScreen()

            else:
                self.checkZoom(events)
                self.exploreScene()
                if self.ShowInfo:
                    self.showInfo()

            pygame.display.update()
            clock.tick()
