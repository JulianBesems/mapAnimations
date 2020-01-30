import numpy as np
import csv, ast, requests, binascii, struct, scipy, pickle, sys, random
import scipy.misc
import scipy.cluster
import urllib.request
from PIL import Image
from io import BytesIO
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from colors import rgb, hex
from colorhash import ColorHash
from sklearn.preprocessing import StandardScaler, MinMaxScaler

count = 0

sys.setrecursionlimit(5000)

class Cell:
    divisions = 2
    def __init__(self, photos, limits):
        self.photos = photos
        self.limits = limits
        self.uniform = self.isUniform()
        if self.uniform:
            self.subcells = None
        else:
            self.subcells = self.split()
        self.neighbours = []

    def isUniform(self):
        difflat = self.limits[1] - self.limits[0]
        difflon = self.limits[3] - self.limits[2]
        if len(self.photos) > 2 and min(difflat, difflon) > 0.00005:
            scaler = MinMaxScaler()
            coordPhotos = []
            for p in self.photos:
                coordPhotos.append(np.array(p[0]))
            coordPhotos = scaler.fit_transform(np.array(coordPhotos))
            xKS = stats.kstest(coordPhotos[:,0], 'uniform')
            yKS = stats.kstest(coordPhotos[:,1], 'uniform')
            if xKS[0] < 0.7 and yKS[0] < 0.7 and xKS[1] > 0.05 and yKS[1] > 0.05:
                """plt.scatter(coordPhotos[:,0], coordPhotos[:,1])
                plt.show()"""

                #print("Uniform")
                #print(self.limits[0], self.limits[2])
                #print(self.limits[1], self.limits[3])
                return True
            else:
                return False
        else:
            return True

    def split(self):
        difflat = self.limits[1] - self.limits[0]
        difflon = self.limits[3] - self.limits[2]
        cellSize = min(difflat,difflon) / self.divisions
        cellDimensions = [difflon/round(difflon/cellSize), difflat/round(difflat/cellSize)]

        grid = [[ [] for _ in range(round(difflat/cellDimensions[1]))]
            for _ in range(round(difflon/cellDimensions[0]))]

        for p in self.photos:
            self.placeInGrid(p, grid, cellDimensions)

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                minlon = self.limits[2] + (i * cellDimensions[0])
                maxlon = minlon + cellDimensions[0]
                minlat = self.limits[0] + (j * cellDimensions[1])
                maxlat = minlat + cellDimensions[1]
                grid[i][j] = Cell(grid[i][j], [minlat, maxlat, minlon, maxlon])
        return grid

    def placeInGrid(self, p, g, cDim):
        y = p[0][0] - self.limits[0]
        x = p[0][1] - self.limits[2]

        xc = int(x/cDim[0])
        if x/cDim[0] == len(g):
            xc -= 1
        yc = int(y/cDim[1])
        if y/cDim[1] == len(g[0]):
            yc -= 1

        if (xc < len(g) and yc < len(g[0])) and (x >= 0 and y >= 0):
            g[xc][yc].append(p)

class LocationGrid:
    def __init__(self):
        self.photos = self.getPhotos()
        self.limits = self.getValues(self.photos)
        #self.photos = self.preprocessPhotos(self.photos)
        self.grid = Cell(self.photos, self.limits)


    def getPhotos(self):
        #with open ("picsSorted.p", 'rb') as fp:
        with open ("preprocessedPhotos-00005.p", 'rb') as fp:
            photos = pickle.load(fp)
        return photos

    def preprocessPhotos(self, photos):
        cellSize = 0.0001
        difflat = self.limits[1] - self.limits[0]
        difflon = self.limits[3] - self.limits[2]
        xCells = int(difflon/cellSize) + 1
        yCells = int(difflat/cellSize) + 1

        grid = np.zeros([xCells, yCells], dtype = object)
        print(grid[0][0])

        for p in photos:
            y = p[0][0] - self.limits[0]
            x = p[0][1] - self.limits[2]

            xc = int(x/cellSize)
            yc = int(y/cellSize)
            if (xc < len(grid) and yc < len(grid[0])) and (x >= 0 and y >= 0) and not grid[xc][yc]:
                grid[xc][yc] = p

        processedPhotos = []
        for a in grid:
            for b in a:
                if b:
                    processedPhotos.append(b)

        print("processed")
        with open("preprocessedPhotos-0001.p", "wb") as fp:
            pickle.dump(processedPhotos, fp, protocol = pickle.HIGHEST_PROTOCOL)
        return processedPhotos


    def getValues(self, photos):
        minlat = 90
        maxlat = -90
        minlon = 180
        maxlon = -180

        for p in photos:
            if p[0][0] < minlat:
                minlat = p[0][0]
            if p[0][0] > maxlat:
                maxlat = p[0][0]
            if p[0][1] < minlon:
                minlon = p[0][1]
            if p[0][1] > maxlon:
                maxlon = p[0][1]

        return(minlat, maxlat, minlon, maxlon)

class Group:
    def __init__(self, l, v):
        self.locations = l
        self.value = v
        self.colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.photos = []

class LocationGroups:
    def __init__(self):
        self.photos = self.getPhotos()
        self.lcGrid = self.getGrid()
        self.limits = self.lcGrid.limits
        self.locations = []
        self.groups = []
        self.getLocations(self.lcGrid.grid, self.locations)
        self.fillNeighbours()
        self.groups.sort(key = lambda x: x.value, reverse = True)
        self.placePhotos()

    def placePhotos(self):
        print(self.photos[0])
        print(self.limits)
        for p in range(len(self.photos)):
            print(p)
            for g in self.groups:
                if self.inGroup(self.photos[p], g):
                    g.photos.append(self.photos[p])


    def inGroup(self, p, g):
        for l in g.locations:
            if (l.limits[0]<= p[0][0] < l.limits[1] and
                l.limits[2]<= p[0][1] < l.limits[3]):
                return True

    def fillNeighbours(self):
        print(len(self.locations))
        i = 0
        for l in self.locations:
            group = self.checkInGroup(l)
            if not self.checkInGroup(l):
                group = Group([l], self.getDensity(l))
                self.groups.append(group)
            print(i, len(self.groups))
            i +=1
            for c in self.locations:
                if not l == c and not (c in group.locations):
                    if self.sharesBorder(l,c):
                        cGroup = self.checkInGroup(c)
                        if cGroup:
                            if self.checkDensity(group.value, cGroup.value):
                                self.mergeGroups(group, cGroup)
                        if self.checkDensity(group.value, self.getDensity(c)):
                            group.locations.append(c)
                            group.value = self.getGroupVal(group)

    def checkDensity(self, v1, v2):
        threshold = 0.12511 * min(v2, v2) + 0.00002
        if abs(v1 - v2) < threshold:
            return True

    def mergeGroups(self, g1, g2):
        g1.locations.extend(g2.locations)
        g1.value = self.getGroupVal(g1)
        self.groups.remove(g2)

    def getGroupVal(self,g):
        sum = 0
        for l in g.locations:
            sum += self.getDensity(l)
        value = sum/len(g.locations)
        return value

    def checkInGroup(self, l):
        for g in self.groups:
            if l in g.locations:
                return g
        return False

    def getDensity(self, l):
        surface = ((l.limits[1]-l.limits[0]) * 100000) * ((l.limits[3]-l.limits[2]) * 100000)
        density = len(l.photos)/surface
        return density


    def sharesBorder(self, l, r):
        lBorders = [[(l.limits[0], l.limits[2]), (l.limits[1], l.limits[2])],
                    [(l.limits[0], l.limits[3]), (l.limits[1], l.limits[3])],
                    [(l.limits[0], l.limits[2]), (l.limits[0], l.limits[3])],
                    [(l.limits[1], l.limits[2]), (l.limits[1], l.limits[3])]
                    ]
        rBorders = [[(r.limits[0], r.limits[2]), (r.limits[1], r.limits[2])],
                    [(r.limits[0], r.limits[3]), (r.limits[1], r.limits[3])],
                    [(r.limits[0], r.limits[2]), (r.limits[0], r.limits[3])],
                    [(r.limits[1], r.limits[2]), (r.limits[1], r.limits[3])]
                    ]

        for lb in lBorders:
            for rb in rBorders:
                if self.checkOverlap(lb, rb):
                    #print(True)
                    return True

    def checkOverlap(self, a, b):
        if a[0][0] == b[0][0] == a[1][0] == b[1][0]:
            return a[1][1] >= b[0][1] and b[1][1] >= a[0][1]
        elif a[0][1] == b[0][1] == a[1][1] == b[1][1]:
            return a[1][0] >= b[0][0] and b[1][0] >= a[0][0]

    """def locationBlocks(self):
        cellSize = 0.00005
        difflat = self.limits[1] - self.limits[0]
        difflon = self.limits[3] - self.limits[2]
        xCells = int(difflon/cellSize) + 1
        yCells = int(difflat/cellSize) + 1

        grid = np.zeros([xCells, yCells], dtype = object)

        for l in locations:
            yl = l.limits[0] - self.limits[0]
            xl = l.limits[2] - self.limits[2]
            yr = l.limits[1] - self.limits[0]
            xr = l.limits[3] - self.limits[2]

            xlc = int(xl/cellSize)
            ylc = int(yl/cellSize)
            xrc = int(xr/cellSize)
            yrc = int(yr/cellSize)
            for x in range(xlc, xrc):
                for y in range(ylc, yrc):
                    if (x < len(grid) and y < len(grid[0])) and not grid[x][y]:
                        grid[x][y] = l
        return grid"""

    def getGrid(self):
        with open ("locationGrid,2,00005,07,005,nr2.p", 'rb') as fp:
            lcGrid = pickle.load(fp)
        return lcGrid

    def getLocations(self, cell, locations):
        if cell.uniform:
            locations.append(cell)
        else:
            for r in cell.subcells:
                for c in r:
                    self.getLocations(c, locations)

    def getPhotos(self):
        with open ("picsSorted.p", 'rb') as fp:
            photos = pickle.load(fp)
        return photos

#lcGroups = LocationGroups()

"""with open ("locationGroupsWP-lin(8,00002).p", 'rb') as gp:
    lGroups = pickle.load(gp)

for gr in lGroups.groups:
    pn = 0
    r = 0
    g = 0
    b = 0
    for l in gr.locations:
        for p in l.photos:
            colour = tuple(hex(p[4]).rgb)
            pn +=1
            r += colour[0]
            g += colour[1]
            b += colour[2]
    if pn == 0:
        gr.colour = (0,0,0)
    else:
        gr.colour = (r/pn, g/pn, b/pn)

with open("locationGroupsWP-lin(8,00002)2.p", "wb") as fp:
    pickle.dump(lGroups, fp, protocol = pickle.HIGHEST_PROTOCOL)"""

"""lcGrid = LocationGrid()
with open("locationGrid,2,00005,07,005,nr2.p", "wb") as fp:
    pickle.dump(lcGrid, fp, protocol = pickle.HIGHEST_PROTOCOL)"""
