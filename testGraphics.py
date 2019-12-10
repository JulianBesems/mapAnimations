import pygame, sys, random, time, csv, ast, requests
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
from logic import SmallDict
import numpy as np
from colors import rgb, hex
from geopy.geocoders import Nominatim
from datetime import datetime
from colorhash import ColorHash

pygame.font.init()
myfont = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 28)
myfontL = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 50)

class Graphics:
    screen_width = 3360 #3360 #1920 #1440 #2560 #1500 #1400 #2000 #1440
    screen_height = 2100 #2100 #1080 #823 #1600 #1000 #800 #1143 #823
    screen_centre = [screen_width/2, screen_height/2]
    buffer = int(screen_height/100)
    ps = int(buffer/10)
    print(ps)

    lim_coord = [12.291284137813543, 45.41960958653527, 12.372472707313529, 45.46473083343668]
    lim_width = lim_coord[2]-lim_coord[0]
    lim_height = lim_coord[3]-lim_coord[1]
    map_centre = [(lim_coord[2]-lim_coord[0])/2 + lim_coord[0],
                    (lim_coord[3]-lim_coord[1])/2 + lim_coord[1]]

    scaling = min(screen_width/lim_width, screen_height/lim_height)

    class Background(pygame.sprite.Sprite):
            def __init__(self, image_file, location):
                pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
                self.image = pygame.image.load(image_file)
                self.rect = self.image.get_rect()
                self.rect.left, self.rect.top = location

    def __init__(self):
        self._screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.photos = []
        with open("imagesCColourA.csv") as csvfile:
            reader = csv.reader(csvfile)
            for r in reader:
                r[0] = ast.literal_eval(r[0])
                if r[4]:
                    radius = 3
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

    def draw_screen(self, screen):
        pygame.init()
        pygame.display.set_caption('flick map 1')

    def map_coordinate(self, latlon):
        x = self.screen_centre[0] + ((float(latlon[0]) - self.map_centre[0]) * self.scaling)
        y = self.screen_centre[1] - ((float(latlon[1]) - self.map_centre[1]) * self.scaling)
        return[int(x),int(y)]

    def draw_post(self, row):
        centre = self.map_coordinate([float(row['longitude']),float(row['latitude'])])
        color = [0,0,0]
        radius = 1
        r = pygame.Rect(centre, (1,1))
        pygame.draw.rect(self._screen, color, r, 0)

    def draw_photo(self, photo, radius):
        centre = self.map_coordinate([photo[0][0], photo[0][1]])
        if photo[4]:
            color = tuple(hex(photo[4]).rgb)
            r = radius
            pygame.draw.circle(self._screen, color, centre, r)

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
            location = locator.reverse(latlon)
            locationText = myfont.render(str(location), False, (255,255,255))
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

    def display(self):
        clock = pygame.time.Clock()
        self._screen.fill(pygame.Color('black'))
        self.draw_screen(self._screen)

        cycle = 0
        pygame.display.update()

        #Background = self.Background('background3360.png', [0,0])

        #self._screen.blit(Background.image, Background.rect)

        buildup = True
        frame = 0
        step = 400
        wait = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            if wait:
                waitText = myfontL.render("VENICE IN FLICKR", False, (255,255,255))
                tw, th = waitText.get_size()
                w, h = (tw + 3 * self.buffer, th + 3 * self.buffer)
                waitBox = pygame.Rect(pygame.Rect((self.screen_centre[0] - int(w/2), self.screen_centre[1] - int(h/2)),
                (w, h)))
                pygame.draw.rect(self._screen, [255,255,255],
                                waitBox, 5)
                self._screen.blit(waitText, (self.screen_centre[0] - int(tw/2), self.screen_centre[1] - int(th/2)))
                if waitBox.collidepoint(pygame.mouse.get_pos()):
                    wait = False
                    self._screen.fill(pygame.Color('black'))

            elif buildup:
                for i in range(frame * step, min(frame*step + step, len(self.photos))):
                    self.draw_photo(self.photos[i], self.ps)
                date = datetime.fromtimestamp(int(self.photos[i][2]))
                gregDate = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
                dateText = myfont.render(gregDate, False, (255,255,255))
                pygame.draw.rect(self._screen, [0,0,0],
                                pygame.Rect((50, self.screen_height - 50), (200, 50)))
                self._screen.blit(dateText, (50, self.screen_height - 50))
                if frame * step >= len(self.photos):
                    buildup = False
                frame += 1
            else:
                self._screen.fill(pygame.Color('black'))
                showingPhoto = None
                connected = []
                for p in self.photos:
                    if p[5].collidepoint(pygame.mouse.get_pos()):
                        self.draw_photo(p, self.ps * 7)
                        connected.extend(self.users[p[1]])
                        pressed = pygame.mouse.get_pressed()[0]
                        if pressed:
                            showingPhoto = p
                    else:
                        self.draw_photo(p, self.ps)
                if showingPhoto:
                    self.showPhoto(showingPhoto)
                    self.showLocation(str(showingPhoto[0][1]) + ", " + str(showingPhoto[0][0]))

                if len(connected) > 1:
                    for i in range(len(connected)-1):
                        colour = self.getUserColor(connected[i][1])
                        self.draw_connection(connected[i][0], connected[i+1][0], colour)
                        self.draw_photo(connected[i], self.ps * 5)
                    self.draw_photo(connected[i+1], self.ps * 5)

            pygame.display.update()
            clock.tick(1000)
