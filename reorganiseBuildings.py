import csv, math

class Building:
    def __init__(self, gr, gVal, box, attractor):
        self.box = box
        self.gVal = gVal
        self.gr = gr
        self.width = self.box[1] - self.box[0]
        self.height = self.box[3] - self.box[2]
        self.centre = [(self.box[0] + self.box[1]) / 2, (self.box[2] + self.box[3]) / 2]
        self.vector = [self.centre[0] - attractor[0], self.centre[1] - attractor[1]]
        self.distance = math.sqrt(self.vector[0]**2 + self.vector[1]**2)
        self.uVector = [self.vector[0]/self.distance, self.vector[1]/self.distance]

    def moveToP(self, point):
        self.centre = point
        self.box = [self.centre[0] - 0.5* self.width, self.centre[0] + 0.5* self.width,
                    self.centre[1] - 0.5* self.height, self.centre[1] + 0.5* self.height]

    def moveByV(self, v):
        self.centre = [self.centre[0] + v[0], self.centre[1] + v[1]]
        self.box = [self.centre[0] - 0.5* self.width, self.centre[0] + 0.5* self.width,
                    self.centre[1] - 0.5* self.height, self.centre[1] + 0.5* self.height]

def collide(b1, b2):
    xOverlap = False
    yOverlap = False
    if (b1.box[0] < b2.box[0] < b1.box[1] or b1.box[0] < b2.box[1] < b1.box[1]
        or b2.box[0] < b1.box[0] < b2.box[1] or b2.box[0] < b1.box[1] < b2.box[1]):
        xOverlap = True
    if (b1.box[2] < b2.box[2] < b1.box[3] or b1.box[2] < b2.box[3] < b1.box[3]
        or b2.box[2] < b1.box[2] < b2.box[3] or b2.box[2] < b1.box[3] < b2.box[3]):
        yOverlap = True
    return(xOverlap and yOverlap)

def collideSet(b1, bSet):
    for b in bSet:
        if collide(b1, b):
            return True

attractor = [3.0878 * 10**6, 1.0155 * 10**6, 0]
buildings = []
with open("locationGroups1.csv") as csvFile:
    reader = csv.reader(csvFile)
    for r in reader:
        b = Building(int(r[0]), float(r[1]), [float(r[2]), float(r[3]), float(r[4]), float(r[5])], attractor)
        buildings.append(b)

for b in buildings:
    b.moveToP(attractor)

movedB = []
factor = 10000
with open("MoveVectors1.csv", "w") as nCsvFile:
    writer = csv.writer(nCsvFile)
    for i in range(len(buildings)):
        print(i)
        b = buildings[i]
        while collideSet(b, movedB):
            b.moveByV([b.uVector[0]*factor, b.uVector[1]*factor])
        movedB.append(b)
        writer.writerow([b.centre[0]- attractor[0], b.centre[1]- attractor[1]])
