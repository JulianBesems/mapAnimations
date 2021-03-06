import numpy as np
import csv, ast, requests, binascii, struct, scipy
import scipy.misc
import scipy.cluster
import urllib.request
from PIL import Image
from io import BytesIO
from io import BytesIO
from os import path

c0 = 0
c2 = 100000
c3 = 50000
c4 = 150000

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

def getColour(imageAddress):
    NUM_CLUSTERS = 5
    response = requests.get(imageAddress)
    try:
        im = Image.open(BytesIO(response.content))
    except OSError:
        return None
    #im.show()
    im = im.resize((150,150))
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

def getAllImages(images):
    count = 0
    for i in images:
        if i[3] and (not path.exists("/Volumes/SeagateSSD/FlickrPhotos/" +  str(i[2]) + "_" + str(i[3].split('/')[-1]))):
            response = requests.get(i[3])
            try:
                im = Image.open(BytesIO(response.content))
                im.thumbnail([256,256], Image.ANTIALIAS)
                imageFile = "/Volumes/SeagateSSD/FlickrPhotos/" +  str(i[2]) + "_" + str(i[3].split('/')[-1])
                im.save(imageFile, "JPEG")
            except OSError:
                pass
        else:
            #print("exists or no url")
            pass
        print(count)
        count +=1


def getAllImageColours(images):
    with open("imagesCColour5.csv", 'a') as newcsvfile:
        writer = csv.writer(newcsvfile)
        for i in range(195290,len(images)):
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
print(len(photos))

#getAllImageColours(photos)
getAllImages(photos)
