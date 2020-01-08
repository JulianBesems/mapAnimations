import numpy as np
import csv, ast, requests, binascii, struct, scipy, pickle
import scipy.misc
import scipy.cluster
import urllib.request
from PIL import Image
from io import BytesIO
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler

count = 0

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

    def isUniform(self):
        difflat = self.limits[1] - self.limits[0]
        difflon = self.limits[3] - self.limits[2]
        if len(self.photos) > 1 and min(difflat, difflon) > 0.00001:
            scaler = MinMaxScaler()
            coordPhotos = []
            for p in self.photos:
                coordPhotos.append(np.array(p[0]))
            coordPhotos = scaler.fit_transform(np.array(coordPhotos))
            xKS = stats.kstest(coordPhotos[:,0], 'uniform')
            yKS = stats.kstest(coordPhotos[:,1], 'uniform')
            if xKS[0] < 0.15 and yKS[0] < 0.15 and xKS[1] > 0.7 and yKS[1] > 0.7:

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

"""lcGrid = LocationGrid()
with open("locationGrid,2,00005,015.p", "wb") as fp:
    pickle.dump(lcGrid, fp, protocol = pickle.HIGHEST_PROTOCOL)"""
