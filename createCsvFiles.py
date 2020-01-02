import csv, ast

fileName = "imagesCColourA.csv"

photos = []
with open(fileName) as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r[0] = ast.literal_eval(r[0])
        if r[4]:
            photos.append(r)
    photos.sort(key = lambda x: x[2])
with open("imagesSorted.csv", 'w') as newCsv:
    writer = csv.writer(newCsv)
    for p in photos:
        writer.writerow(p)
