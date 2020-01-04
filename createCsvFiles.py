import csv, ast, pickle
from colors import rgb, hex

with open ("picsSorted.p", 'rb') as fp:
    photos = pickle.load(fp)

def getUsers(photos):
    u = []
    for p in photos:
        user = (p[1], [])
        if user not in u:
            u.append(user)
    users = {key : value for (key, value) in u}
    for i in photos:
        users[i[1]].append(i)
    return users

users = getUsers(photos)

with open("userDict.p", "wb") as fp:
    pickle.dump(users, fp, protocol = pickle.HIGHEST_PROTOCOL)
"""
with open ("userDict.p", 'rb') as fp:
    data = pickle.load(fp)

print(data["67011548@N00"])

fileName = "imagesCColourA.csv"

photos = []
"""
def getUsers(photos):
    u = []
    for p in photos:
        user = (p[1], [])
        if user not in u:
            u.append(user)
    users = {key : value for (key, value) in u}
    for i in photos:
        users[i[1]].append(i)
    return users
"""
with open(fileName) as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r[0] = [ast.literal_eval(r[0])[1], ast.literal_eval(r[0])[0]]
        if r[4]:
            try:
                color = tuple(hex(r[4]).rgb)
                photos.append(r)
            except ValueError:
                print(r[4])
    photos.sort(key = lambda x: x[2])

with open("picsSorted.p", "wb") as fp:
    pickle.dump(photos, fp, protocol = pickle.HIGHEST_PROTOCOL)

with open ("picsSorted.p", 'rb') as fp:
    photos = pickle.load(fp)

with open ("userDict.p", 'rb') as fp:
    users = pickle.load(fp)

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


difflat = maxlat - minlat
difflon = maxlon - minlon
print([minlat, maxlat, minlon, maxlon])
print([difflat, difflon])

cellSize = 0.0001

nrCellsX = int(difflon/cellSize) + 1
nrCellsY = int(difflat/cellSize) + 1
print([nrCellsX, nrCellsY])

grid = [[ [] for _ in range(nrCellsY)]
            for _ in range(nrCellsX)]

def placeInGrid(p, g):
    y = p[0][0] - minlat
    x = p[0][1] - minlon
    xc = int(x/cellSize)
    yc = int(y/cellSize)
    if (xc < nrCellsX and yc < nrCellsY) and (xc > 0 and yc > 0):
        g[xc][yc].append(p)


for p in photos:
    placeInGrid(p, grid)

with open("photoGrid.p", "wb") as fp:
    pickle.dump(grid, fp, protocol = pickle.HIGHEST_PROTOCOL)



with open ("photoGrid.p", 'rb') as fp:
    grid = pickle.load(fp)


def exportGridtoRhino(grid):
    with open("VeniceGrid2.csv", 'w') as newcsvfile:
        writer = csv.writer(newcsvfile)
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j]:
                    writer.writerow([i, j, len(grid[i][j])])

exportGridtoRhino(grid)"""
