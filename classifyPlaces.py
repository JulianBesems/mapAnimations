import numpy as np
import csv, ast, requests, binascii, struct, scipy
import scipy.misc
import scipy.cluster
import urllib.request
from PIL import Image
from io import BytesIO

lim_coord = [12.291284137813543, 45.41960958653527, 12.372472707313529, 45.46473083343668]
lim_width = lim_coord[2]-lim_coord[0]
lim_height = lim_coord[3]-lim_coord[1]
cellSize = lim_width/3360*5

nrCellsX = int(lim_width/cellSize)
nrCellsY = int(lim_height/cellSize)


grid = [[ [] for _ in range(nrCellsY)]
            for _ in range(nrCellsX)]

def getPhotos(fileName):
    d = []
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            d.append(row)
    csvfile.close()
    for k in d:
        k[0] = ast.literal_eval(k[0])
        k[2] = int(k[2])
    return d

def placeInGrid(p, g):
    x = p[0][0] - lim_coord[0]
    y = p[0][1] - lim_coord[1]
    xc = int(x/cellSize)
    yc = int(y/cellSize)
    if (xc < nrCellsX and yc < nrCellsY) and (xc > 0 and yc > 0):
        if g[xc][yc] == []:
            g[xc][yc] = [[p], None]
        else:
            g[xc][yc][0].append(p)

def fillGrid(pics,g):
    for p in pics:
        placeInGrid(p, g)

def index_2d(grid, c):
    for i, x in enumerate(grid):
        if c in x:
            return (i, x.index(c))

def getFilledIndices(grid):
    indices = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j]:
                indices.append((i,j))
    return indices

def isInGroup(groups, c):
    for g in groups:
        if c in g:
            return g

def getSurroundingCells(i,j):
    cells = []
    if i > 0:
        cells.append((i-1,j))
        if j > 0:
            cells.append((i-1,j-1))
            cells.append((i,j-1))
        if j < nrCellsY - 1:
            cells.append((i-1,j+1))
            cells.append((i,j+1))
    if i < nrCellsX - 1:
        cells.append((i + 1, j))
        if j > 0:
            cells.append((i+1, j-1))
        if j < nrCellsY - 1:
            cells.append((i+1, j+1))
    return cells

def makeLocations(grid):
    groups = []
    cell = None
    for i in range(len(grid)):
        print(str(i) + "/" + str(nrCellsX) + "    groups: " + str(len(groups)))
        for j in range(len(grid[0])):
            cell = grid[i][j]
            if cell:
                if cell[1] == None:
                    sCells = getSurroundingCells(i,j)
                    adjGroups = []
                    adjCells = []
                    for s in sCells:
                        if grid[s[0]][s[1]]:
                            g = grid[s[0]][s[1]][1]
                            if g != None and g not in adjGroups:
                                adjGroups.append(g)
                            else:
                                adjCells.append(grid[s[0]][s[1]])
                    if len(adjGroups) > 0:
                        newGroup = []
                        for g in adjGroups:
                            newGroup.extend(g)
                            groups.remove(g)
                        newGroup.append(cell)
                        newGroup.extend(adjCells)
                        groups.append(newGroup)
                        for c in newGroup:
                            c[1] = newGroup
                    elif len(adjCells) > 0:
                        adjCells.append(cell)
                        newGroup = adjCells
                        groups.append(newGroup)
                        for c in newGroup:
                            c[1] = newGroup

    return groups

def getColour(imageAddress):
    NUM_CLUSTERS = 5
    response = requests.get(imageAddress)
    im = Image.open(BytesIO(response.content))
    #im.show()
    im.resize((100,100))
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    #print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    #print('cluster centres:\n', codes)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

    index_max = scipy.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    #print('most frequent is %s (#%s)' % (peak, colour))
    return colour

def getAllImageColours(images):
    with open("imagesCColour.csv", 'a') as newcsvfile:
        writer = csv.writer(newcsvfile)
        for i in range(360,len(images)):
            if images[i][3]:
                try:
                    c = getColour(images[i][3])
                except IndexError:
                    c = None
            else:
                c = None
            images[i].append(c)
            writer.writerow(images[i])
            print("image: " + str(i) + "/" + str(len(images)))

photos = getPhotos('imagesC.csv')
print("got Photos")

#getAllImageColours(photos)

fillGrid(photos, grid)
locs = makeLocations(grid)
print(len(locs))
maxLoc = []
for l in locs:
    if len(l) > len(maxLoc):
        maxLoc = l
locs.sort(key=len, reverse = True)
for i in range(10):
    print(len(locs[10]))
