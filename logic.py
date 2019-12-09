import time, random, datetime, pygame, csv, ast
from collections import OrderedDict

class Dict:
    def __init__(self, fileName):
        self.dict = self.readDict(fileName)
        self.images = self.getImages()
        self.users = self.getUsers()
        self.fillUsers()
        #self.exportUsers()

    def readDict(self, fileName):
        d = []
        with open(fileName) as csvfile:
            reader = csv.DictReader(csvfile)
            key = reader.fieldnames
            for row in reader:
                d.append(row)
        return d

    def getImages(self):
        i = []
        for row in self.dict:
            img = [[float(row['longitude']),float(row['latitude'])], row['owner'],
            row['dateupload'], row['url_c']]
            i.append(img)
        return i

    def getUsers(self):
        u = []
        for row in self.dict:
            user = (row['owner'], [])
            if user not in u:
                u.append(user)
        users = {key : value for (key, value) in u}
        return users

    def fillUsers(self):
        for i in self.images:
            self.users[i[1]].append(i)

    def exportUsers(self):
        with open("usersC.csv", 'w') as newcsvfile:
            writer = csv.writer(newcsvfile)
            keys = []
            vals = []
            for k in self.users:
                keys.append(k)
                vals.append(self.users[k])
            writer.writerow(keys)
            writer.writerow(vals)

class SmallDict:
    def __init__(self, fileName):
        self.dict = self.readDict(fileName)
        self.users = self.getUsers()

    def readDict(self, fileName):
        d = []
        with open(fileName) as csvfile:
            reader = csv.DictReader(csvfile)
            key = reader.fieldnames
            for row in reader:
                d.append(row)
            for k in d[0]:
                d[0][k] = ast.literal_eval(d[0][k])
        return d[0]

    def getUsers(self):
        users = []
        for u in self.dict:
            users.append(u)
        return users
