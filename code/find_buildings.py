import csv

wkt_railway = ''
qq_railway = []
with open('railway.csv') as railway_csv:
    railway_spamreader = csv.reader(railway_csv)
    for railway_row in railway_spamreader:
        qq_railway.append(railway_row)

wkt_railway = qq_railway[1][0]