import pygame, sys, random, time
from logic import SmallDict
import numpy as np

pygame.font.init()
myfont = pygame.font.Font('/Users/julianbesems/Library/Fonts/HELR45W.ttf', 28)

class Graphics:
    screen_width = 3360 #3360 #1920 #1440 #2560 #1500 #1400 #2000 #1440
    screen_height = 2100 #2100 #1080 #823 #1600 #1000 #800 #1143 #823
    screen_centre = [screen_width/2, screen_height/2]

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
        self.dictionary = SmallDict('users.csv')

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

    def draw_coordinates(self, coord, color):
        centre = self.map_coordinate(coord)
        radius = 2 #int(self.screen_height/1000)
        r = pygame.Rect(centre, (2,2))
        pygame.draw.circle(self._screen, color, centre, radius)
        #pygame.draw.rect(self._screen, color, r, 0)

    def draw_connection(self, c1, c2):
        p1 = self.map_coordinate(c1)
        p2 = self.map_coordinate(c2)
        pygame.draw.line(self._screen, [100,100,100, 0.5], p1, p2, 1)


    def display(self):

        clock = pygame.time.Clock()
        self._screen.fill(pygame.Color('black'))
        self.draw_screen(self._screen)

        cycle = 0
        pygame.display.update()

        usr = self.dictionary.users
        print(len(usr))

        #Background = self.Background('background3360.png', [0,0])

        #self._screen.blit(Background.image, Background.rect)

        buildup = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            if buildup:
                self._screen.fill(pygame.Color('black'))
                #self._screen.blit(Background.image, Background.rect)

            entries = []
            for i in range(50):
                entries.append(self.dictionary.dict[usr[cycle]])
                if cycle < len(usr)-1:
                    cycle += 1

            if buildup:
                for e in entries:
                    if len(e) > 1:
                        for i in range(len(e)-1):
                            self.draw_connection(e[i], e[i+1])

            for e in entries:
                for c in e:
                    self.draw_coordinates(c, [250,250,250])

            userText = myfont.render(usr[cycle], False, (0,0,0))
            #self._screen.blit(userText, (20, 20))


            pygame.display.update()

            if cycle < len(usr)-1:
                cycle += 1
            else:
                if buildup:
                    buildup = False
                else:
                    buildup = True
                cycle = 0
            print(cycle)
            clock.tick(1000)
