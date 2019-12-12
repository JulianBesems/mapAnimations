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
           "generate spatial configurations, where each outcome is defined by the how one specific input",
           "relates to the wider context that informs the recommender system."]

class Graphics:
    screen_width = 3360 #3360 #1920 #1440 #2560 #1500 #1400 #2000 #1440
    screen_height = 2100 #2100 #1080 #823 #1600 #1000 #800 #1143 #823
    screen_centre = [screen_width/2, screen_height/2]
    buffer = int(screen_height/100)
    ps = int(buffer/10)

    #lim_coord = [12.291284137813543, 45.41960958653527, 12.372472707313529, 45.46473083343668]
    #lim_coord = [12.291284137813543, 45.41960958653527, 12.363478132855798, 45.46473083343668]
    lim_coord = [12.29609707081636, 45.41960958653527, 12.368291065858616, 45.46473083343668]
    lim_width = lim_coord[2]-lim_coord[0]
    lim_height = lim_coord[3]-lim_coord[1]
    map_centre = [(lim_coord[2]-lim_coord[0])/2 + lim_coord[0],
                    (lim_coord[3]-lim_coord[1])/2 + lim_coord[1]]

    #cellSize = lim_width/3360
    #grid = [[ [] for _ in range(2100)] for _ in range(3360)]

    scaling = min(screen_width/lim_width, screen_height/lim_height)
    monthRange = [0,12]
    yearRange = [2003, 2019]

    fileName = "imagesCColourA.csv"

    class Background(pygame.sprite.Sprite):
            def __init__(self, image_file, location):
                pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
                self.image = pygame.image.load(image_file)
                self.rect = self.image.get_rect()
                self.rect.left, self.rect.top = location

    def __init__(self):
        self._screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.photos = []
        with open(self.fileName) as csvfile:
            reader = csv.reader(csvfile)
            for r in reader:
                r[0] = ast.literal_eval(r[0])
                if r[4]:
                    radius = 2 * self.ps
                    centre = self.map_coordinate([r[0][0], r[0][1]])
                    centre[0] -= 1
                    centre[1] -= 1
                    try:
                        color = tuple(hex(r[4]).rgb)
                        circle = pygame.Rect(centre, (radius,radius))
                        r.append(circle)
                        self.photos.append(r)
                    except ValueError:
                        pass
        self.photos.sort(key = lambda x: x[2])
        self.users = self.getUsers(self.photos)
        #fillGrid(self.photos, self.grid)
        #self.locs = makeLocations(self.grid)
        #self.locs.sort(key = len, reverse = True)
        #print(len(self.locs[0]))

    def reposPhotos(self):
        for p in self.photos:
            radius = 2 * self.ps
            centre = self.map_coordinate([p[0][0], p[0][1]])
            centre[0] -= 1
            centre[1] -= 1
            circle = pygame.Rect(centre, (radius,radius))
            p[-1] = circle

    def draw_screen(self, screen):
        pygame.init()
        pygame.display.set_caption('flick map 1')

    def map_coordinate(self, latlon):
        x = self.screen_centre[0] + ((float(latlon[0]) - self.map_centre[0]) * self.scaling)
        y = self.screen_centre[1] - ((float(latlon[1]) - self.map_centre[1]) * self.scaling)
        return[int(x),int(y)]

    def inv_coordinates(self, point):
        lat = (point[0] - self.screen_centre[0])/self.scaling + self.map_centre[0]
        lon = (point[1] - self.screen_centre[1])/self.scaling + self.map_centre[1]
        return (lat, lon)

    def draw_post(self, row):
        centre = self.map_coordinate([float(row['longitude']),float(row['latitude'])])
        color = [0,0,0]
        radius = 1
        r = pygame.Rect(centre, (1,1))
        pygame.draw.rect(self._screen, color, r, 0)

    def draw_photo(self, photo, radius, shape, c = None):
        centre = self.map_coordinate([photo[0][0], photo[0][1]])
        if photo[4]:
            if c:
                color = c
            else:
                color = tuple(hex(photo[4]).rgb)
            r = radius
            if shape == "circle":
                pygame.draw.circle(self._screen, color, centre, r)
            if shape == "cross":
                pygame.draw.line(self._screen, color, (centre[0]-r, centre[1]), (centre[0]+r, centre[1]), int(r/2))
                pygame.draw.line(self._screen, color, (centre[0], centre[1]-r), (centre[0], centre[1]+r), int(r/2))

    def draw_coordinates(self, coord, color):
        centre = self.map_coordinate(coord)
        radius = 2 #int(self.screen_height/1000)
        r = pygame.Rect(centre, (2,2))
        pygame.draw.circle(self._screen, color, centre, radius)
        #pygame.draw.rect(self._screen, color, r, 0)

    def draw_connection(self, c1, c2, colour):
        p1 = self.map_coordinate(c1)
        p2 = self.map_coordinate(c2)
        pygame.draw.line(self._screen, colour, p1, p2, 1)

    def showPhoto(self, p):
        imageUrl = p[3]
        try:
            imageStr = urlopen(imageUrl).read()
            im = BytesIO(imageStr)
            #im = im.resize((150,150))
            photo = pygame.image.load(im)
            rect = photo.get_rect()
            pygame.draw.line(self._screen, tuple(hex(p[4]).rgb), p[5].topleft,
            rect.bottomleft, 1)
            pygame.draw.line(self._screen, tuple(hex(p[4]).rgb), p[5].topleft,
            rect.topright, 1)
            pygame.draw.line(self._screen, tuple(hex(p[4]).rgb), p[5].topleft,
            rect.bottomright, 1)
            self._screen.blit(photo, [0,0])
        except OSError:
            return None

    def showLocation(self, latlon):
        locator = Nominatim(user_agent="myGeocoder")
        try:
            location = str(locator.reverse(latlon))
            locationText = myfont.render(location.partition(",")[0], False, (255,255,255))
            self._screen.blit(locationText, (50, self.screen_height - 50))
        except:
            pass

    def getUsers(self, photos):
        u = []
        for p in photos:
            user = (p[1], [])
            if user not in u:
                u.append(user)
        users = {key : value for (key, value) in u}
        for i in photos:
            users[i[1]].append(i)
        return users

    def getUserColor(self, user):
        c = ColorHash(user)
        return(c.rgb)

    def drawMouse(self):
        mouseP = pygame.mouse.get_pos()
        pygame.draw.line(self._screen, (100,100,100), (mouseP[0], 0), (mouseP[0], self.screen_height), 1)
        pygame.draw.line(self._screen, (100,100,100), (0, mouseP[1]), (self.screen_width, mouseP[1]), 1)
        lon, lat = self.inv_coordinates(mouseP)
        latText = myfontS.render(str(lat), False, (255,255,255))
        lonText = myfontS.render(str(lon), False, (255,255,255))
        latWidth = latText.get_size()[0]
        self._screen.blit(latText, (self.screen_width - latWidth - self.buffer, mouseP[1] + self.buffer))
        self._screen.blit(lonText, (mouseP[0] + self.buffer, self.buffer))

    def timeSlider(self):
        widthm = self.buffer * 12
        widthy = self.buffer * (2019-2003)
        startxm = self.screen_centre[0] - int(widthm/2)
        startxy = self.screen_centre[0] - int(widthy/2)
        mStep = int(widthm/12)
        yStep = int(widthy/(2019-2003))
        mouseP = pygame.mouse.get_pos()
        for i in range(12):
            box = pygame.Rect((startxm + i*mStep, self.buffer * 5 - 3 * self.ps),
                            (mStep, 6 * self.ps))
            if box.collidepoint(mouseP):
                mText = myfontS.render(str(i+1), False, (255,255,255))
                self._screen.blit(mText, (box.left + 3*self.ps, self.buffer * 5 + 4 * self.ps))
                if pygame.mouse.get_pressed()[0] and i < self.monthRange[1]:
                    self.monthRange[0] = i
                if pygame.mouse.get_pressed()[2] and i >= self.monthRange[0]:
                    self.monthRange[1] = i+1

        for i in range((2019-2003)):
            box = pygame.Rect((startxy + i*yStep, self.buffer * 3 - 3 * self.ps),
                            (yStep, 6 * self.ps))
            if box.collidepoint(mouseP):
                yText = myfontS.render(str(i+2003), False, (255,255,255))
                self._screen.blit(yText, (box.left, self.buffer * 3 + 4 * self.ps))
                if pygame.mouse.get_pressed()[0] and (i+2003) < self.yearRange[1]:
                    self.yearRange[0] = i+2003
                if pygame.mouse.get_pressed()[2] and (i+2003) >= self.yearRange[0]:
                    self.yearRange[1] = i+2004

        yRect = pygame.Rect((startxm + self.monthRange[0] * mStep, self.buffer * 5 - 3*self.ps),
                        ((self.monthRange[1]-self.monthRange[0]) * mStep, 6 * self.ps))
        mRect = pygame.Rect((startxy + (self.yearRange[0] - 2003) * yStep, self.buffer * 3 - 3*self.ps),
                        ((self.yearRange[1]-self.yearRange[0]) * yStep, 6 * self.ps))
        pygame.draw.rect(self._screen, (100,100,100), yRect)
        pygame.draw.rect(self._screen, (100,100,100), mRect)

        pygame.draw.line(self._screen, (250,250,250), (startxm, self.buffer * 5),
                        (startxm + widthm, self.buffer * 5), self.ps)
        pygame.draw.line(self._screen, (250,250,250), (startxy, self.buffer * 3),
                        (startxy + widthy, self.buffer * 3), self.ps)
        for i in range(13):
            pygame.draw.line(self._screen, (200,200,200), (startxm + i*mStep, self.buffer * 5 - 3 * self.ps),
                            (startxm + i*mStep, self.buffer * 5 + 3 * self.ps), 1)
        for j in range((2019-2003)+1):
            pygame.draw.line(self._screen, (200,200,200), (startxy + j*yStep, self.buffer * 3 - 3 * self.ps),
                            (startxy + j*yStep, self.buffer * 3 + 3 * self.ps), 1)

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
        self.reposPhotos()


    def zoom(self, arg):
        ratio = self.screen_width/self.screen_height
        pos = pygame.mouse.get_pos()
        rate = 1/20
        sW = self.lim_width * rate
        sH = self.lim_height * rate
        if arg == "in":
            self.lim_coord = [self.lim_coord[0] + sW, self.lim_coord[1] + sH,
                            self.lim_coord[2] - sW, self.lim_coord[3] - sH]
            #lim_coord = [12.305722936821994, 45.41960958653527, 12.377916931864249, 45.46473083343668]
        if arg == "out":
            self.lim_coord = [self.lim_coord[0] - sW, self.lim_coord[1] - sH,
                            self.lim_coord[2] + sW, self.lim_coord[3] + sH]

        self.lim_width = self.lim_coord[2]-self.lim_coord[0]
        self.lim_height = self.lim_coord[3]-self.lim_coord[1]
        self.map_centre = [(self.lim_coord[2]-self.lim_coord[0])/2 + self.lim_coord[0],
                        (self.lim_coord[3]-self.lim_coord[1])/2 + self.lim_coord[1]]

        self.scaling = min(self.screen_width/self.lim_width, self.screen_height/self.lim_height)
        self.reposPhotos()

        vr = ((pos[0] - self.screen_width / 2 )/ (self.screen_width/2), (self.screen_height /2 - pos [1])/(self.screen_height /2))
        self.move(vr, rate/2)

    def loadingScreen(self):
        self._screen.fill(pygame.Color('black'))
        loadText = myfontL.render("LOADING", False, (255,255,255))
        tw, th = loadText.get_size()
        self._screen.blit(loadText, (self.screen_centre[0] - int(tw/2), self.screen_centre[1] - int(th/2)))
        pygame.display.update()

    def countData(self):
        self.loadingScreen()
        shownPhotos = []
        shownUsers = []
        for p in self.photos:
            date = datetime.fromtimestamp(int(p[2]))
            if ((self.yearRange[0] <= date.year <= self.yearRange[1]) and
                (self.monthRange[0] <= date.month <= self.monthRange[1]) and
                (self.lim_coord[0] < p[0][0] < self.lim_coord[2]) and
                (self.lim_coord[1] < p[0][1] < self.lim_coord[3])):
                shownPhotos.append(p)
                if not p[1] in shownUsers:
                    shownUsers.append(p[1])
        return (shownPhotos, shownUsers)

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


    def display(self):
        clock = pygame.time.Clock()
        self._screen.fill(pygame.Color('black'))
        self.draw_screen(self._screen)

        cycle = 0
        pygame.display.update()


        buildup = True
        frame = 0
        step = 600
        wait = True
        ShowData = False
        Recommend = False
        ShowInfo = False
        shownUsers = []
        shownPhotos = []
        chosenPhotos = []

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_d:
                        if ShowData:
                            ShowData = False
                        else:
                            #shownPhotos, shownUsers = self.countData()
                            ShowData = True
                    if event.key == pygame.K_RETURN and chosenPhotos:
                        if Recommend:
                            Recommend = False
                        else:
                            Recommend = True

            if pygame.mouse.get_pressed()[1]:
                buildup = True
                frame = 0
                wait = True
                self._screen.fill(pygame.Color('black'))

            if wait:
                waitText = myfontL.render("VENICE IN FLICKR", False, (255,255,255))
                tw, th = waitText.get_size()
                w, h = (tw + 3 * self.buffer, th + 3 * self.buffer)
                waitBox = pygame.Rect((self.screen_centre[0] - int(w/2), self.screen_centre[1] - int(h/2)),
                (w, h))
                pygame.draw.rect(self._screen, [255,255,255],
                                waitBox, 3* self.ps - 1)
                self._screen.blit(waitText, (self.screen_centre[0] - int(tw/2), self.screen_centre[1] - int(th/2)))
                if waitBox.collidepoint(pygame.mouse.get_pos()):
                    wait = False
                    self._screen.fill(pygame.Color('black'))

            elif buildup:
                for i in range(frame * step, min(frame*step + step, len(self.photos))):
                    self.draw_photo(self.photos[i], self.ps, "circle")
                date = datetime.fromtimestamp(int(self.photos[i][2]))
                gregDate = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
                dateText = myfont.render(gregDate, False, (255,255,255))
                pygame.draw.rect(self._screen, [0,0,0],
                                pygame.Rect((50, self.screen_height - 50), (200, 50)))
                self._screen.blit(dateText, (50, self.screen_height - 50))
                if frame * step >= len(self.photos):
                    buildup = False
                frame += 1

            elif ShowData:
                self._screen.fill(pygame.Color('black'))
                photoText = myfontL.render("PHOTOS: " +str(len(self.photos)), False, (255,255,255))
                userText = myfontL.render( "USERS :  " +  str(len(self.users)), False, (255,255,255))
                ptw, pth = photoText.get_size()
                utw, uth = photoText.get_size()

                self._screen.blit(photoText, (self.screen_centre[0] - int(ptw/2), self.screen_centre[1] - int(pth/2) - 2*self.buffer))
                self._screen.blit(userText, (self.screen_centre[0] - int(ptw/2), self.screen_centre[1] - int(pth/2) + 2*self.buffer))

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_d:
                            #self.loadingScreen()
                            ShowData = False


            elif Recommend:
                self._screen.fill(pygame.Color('black'))
                connected = []

                for p in chosenPhotos:
                    connected.extend(self.users[p[1]])
                    connected.remove(p)

                groups = []
                for a in connected:
                    group = [a]
                    for b in connected:
                        ab = [a[5][0]-b[5][0], a[5][1] - b[5][1]]
                        if math.sqrt(ab[0]**2 + ab[1]**2) < (self.buffer * 3):
                            group.append(b)
                            connected.remove(b)
                    groups.append(group)

                if len(groups) > 0:
                    for g in groups:
                        if len(g) >= 2:
                            for i in range(len(g)-1):
                                self.draw_connection(g[i][0], g[i+1][0], (200,200,200))
                            #poly = geometry.Polygon(points)
                            #pygame.draw.polygon(self._screen, (100,100,100), poly.exterior.coords)

                    for g in groups:
                        for c in g:
                            self.draw_photo(c, self.ps * 3, "cross", (200,200,200))

                if len(chosenPhotos) > 1:
                    for i in range(len(chosenPhotos)-1):
                        self.draw_connection(chosenPhotos[i][0], chosenPhotos[i+1][0], (200,50,50))

                for p in chosenPhotos:
                    self.draw_photo(p, self.ps * 7, "cross", (200,50,50))


                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            Recommend = False
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

            else:
                mouseP = pygame.mouse.get_pos()
                self._screen.fill(pygame.Color('black'))
                showingPhoto = None
                chosenPhoto = None
                connected = []
                for p in self.photos:
                    date = datetime.fromtimestamp(int(p[2]))
                    if ((self.yearRange[0] <= date.year <= self.yearRange[1]) and
                        (self.monthRange[0] <= date.month <= self.monthRange[1])):
                        if p[5].collidepoint(pygame.mouse.get_pos()):
                            self.draw_photo(p, self.ps * 7, "cross")
                            connected.extend(self.users[p[1]])
                            pressedL = pygame.mouse.get_pressed()[0]
                            pressedR = pygame.mouse.get_pressed()[2]
                            if pressedL:
                                showingPhoto = p
                            if pressedR:
                                if p not in chosenPhotos:
                                    chosenPhoto = p
                        else:
                            self.draw_photo(p, self.ps, "circle")
                if chosenPhoto:
                    chosenPhotos.append(chosenPhoto)
                if showingPhoto:
                    self.showPhoto(showingPhoto)
                    self.showLocation(str(showingPhoto[0][1]) + ", " + str(showingPhoto[0][0]))

                if len(connected) > 1:
                    for i in range(len(connected)-1):
                        colour = self.getUserColor(connected[i][1])
                        self.draw_connection(connected[i][0], connected[i+1][0], colour)
                        self.draw_photo(connected[i], self.ps * 5, "cross")
                    self.draw_photo(connected[i+1], self.ps * 5, "cross")
                self.drawMouse()
                self.timeSlider()

                if chosenPhotos:
                    for c in chosenPhotos:
                        self.draw_photo(c, self.ps * 7, "cross")

                if ShowInfo:
                    self.showInfo()

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

                        if event.key == pygame.K_RETURN and chosenPhotos:
                            if Recommend:
                                Recommend = False
                            else:
                                Recommend = True

                        if event.key == pygame.K_BACKSPACE:
                            if chosenPhotos:
                                chosenPhotos.remove(chosenPhotos[-1])

                        if event.key == pygame.K_d:
                            if ShowData:
                                ShowData = False
                            else:
                                #shownPhotos, shownUsers = self.countData()
                                ShowData = True

                        if event.key == pygame.K_i:
                            if ShowInfo:
                                ShowInfo = False
                            else:
                                #shownPhotos, shownUsers = self.countData()
                                ShowInfo = True

                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()



                """if pygame.key.get_pressed()[pygame.K_SPACE]:
                    self._screen.fill(pygame.Color('black'))
                    for g in self.locs:
                        if len(g) > 300:
                            print(g[0][1])
                            for c in g:
                                r = random.randint(0,255)
                                g = random.randint(0,255)
                                b = random.randint(0,255)
                                pygame.draw.rect(self._screen, [r,g,b],
                                            (c[1], (1,1)))"""



            pygame.display.update()
            clock.tick(1000)
