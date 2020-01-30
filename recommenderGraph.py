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
from classifyPlaces2 import LocationGrid, Cell, Group, LocationGroups

class CooccurenceMatrix():
    def __init__(self, usrDict, lcGrp):
        self.users = self.getUserDict(usrDict)
        self.lcGroups = self.getLcGroups(lcGrp).groups
        self.ccMatrix = self.constructCcMatrix()

    def getGroupUsers(self, group):
        photos = group.photos
        users = []
        for p in photos:
            if not p[1] in users:
                users.append(p[1])
        return set(users)

    def constructCcMatrix(self):
        maxCooccurence = 0

        nrGroups = len(self.lcGroups)

        allGroupUsers = []
        for i in range(nrGroups):
            allGroupUsers.append(self.getGroupUsers(self.lcGroups[i]))

        cooccurence_matrix = np.matrix(np.zeros(shape=(nrGroups, nrGroups)), float)

        for i in range(nrGroups):
            users_i = allGroupUsers[i]

            for j in range(nrGroups):
                users_j = allGroupUsers[j]

                users_intersection = users_i.intersection(users_j)

                if len(users_intersection) > 0:
                    users_union = users_i.union(users_j)
                    value = ((len(users_intersection)/len(users_j)) + (len(users_intersection)/len(users_union))) / 2

                    cooccurence_matrix[i, j] = value

                    if value > maxCooccurence:
                        maxCooccurence = value

                else:
                    cooccurence_matrix[i, j] = 0
        print(maxCooccurence)

        return cooccurence_matrix

    def getUserDict(self, filename):
        with open (filename, 'rb') as fp:
            userDict = pickle.load(fp)
        return userDict

    def getLcGroups(self, filename):
        with open (filename, 'rb') as gp:
            lcGroups = pickle.load(gp)
        return lcGroups


"""ccMatrix = CooccurenceMatrix("userDict.p", "locationGroupsWP2-lin(8,00002).p")
with open("ccMatrixDirProp6.p", "wb") as fp:
    pickle.dump(ccMatrix, fp, protocol = pickle.HIGHEST_PROTOCOL)"""
