import pickle

l1a = (45.44100994935137, 12.35640913750912)
l2a = (45.438087811458796, 12.380276672956605)

l1 = (45.44101094935137, 12.35640813750912)
l2 = (45.438086811458796, 12.380277672956605)

with open ("picsSorted.p", 'rb') as fp:
    photos = pickle.load(fp)
for p in photos:
    if p[0][0] > l2a[0] and p[0][0] < l1a[0] and p[0][1] > l1a[1] and p[0][1] < l2a[1]:
        print(p[3])
