import math
from wktparser import WKTUnSerializer
import csv


class Point(object):
    def __init__(self, x, y):
        """Constructor. 
        Takes the x and y coordinates to define the Point instance.
        """
        self.x = float(x)
        self.y = float(y)
    def distance(self, other):
        """Returns cartesian distance between self and other Point
        """
        x1 = self.x
        y1 = self.y
        x2 = other.x
        y2 = other.y
        return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))



class Vector(object):
    def __init__(self, start_point, end_point):
        self.start, self.end = start_point, end_point
        self.x = end_point.x - start_point.x
        self.y = end_point.y - start_point.y
    def negative(self):
        return Vector(self.end, self.start)
    def vector_product(self, vec):
        return self.x * vec.y - vec.x * self.y



class building(object):
    """docstring for building"""
    # eg. shape_wkt = [[1 1, 2 2, 1 3, 0 2]]
    def __init__(self, shape_wkt, height):
        self.shape = shape_wkt
        self.height = height
    # check whether building intersects line segment (p1, p2)
    # https://segmentfault.com/a/1190000004457595
    def intersects(self, p1, p2):
        # no need to consider the case where p1 or p2 inside the building: nb!
        A = p1
        B = p2
        for polygon in self.shape: # may contain outer/inner
            n = len(polygon)
            for i in range(n):
                C = Point(polygon[i][0], polygon[i][1])
                D = Point(polygon[(i+1)%n][0], polygon[(i+1)%n][1])
                AC = Vector(A, C)
                AD = Vector(A, D)
                BC = Vector(B, C)
                BD = Vector(B, D)
                CA = AC.negative()
                CB = BC.negative()
                DA = AD.negative()
                DB = BD.negative()
                ZERO = 1e-9
                if (AC.vector_product(AD) * BC.vector_product(BD) <= ZERO) and (CA.vector_product(CB) * DA.vector_product(DB) <= ZERO):
                    return True
        return False






class delft_noise(object):
    """docstring for delft_noise"""
    # railway is a list of points
    # buildings is a list of building
    def __init__(self, railway, buildings):
        self.railway = railway
        self.buildings = buildings
        self.source_noise = 102
        self.remove_leq_10 = 2
        self.remove_geq_10 = 5
    
    
    # calculate the noise
    def cal_noise(self, p):
        # calculate the distance between p and railway
        dist_railway_list = [p.distance(pts) for pts in self.railway]
        # distance between p and the railway
        dist_railway = min(dist_railway_list)
        # which pt on the railway gives the min?
        pt_on_railway = self.railway[dist_railway_list.index(dist_railway)]
        # check whether (pt_on_railway, p) intersects buildings
        total_noise = self.source_noise - 16*math.log(dist_railway)/math.log(10) + 9
        for tatemono in self.buildings:
            # if intersect, substract by shading
            if tatemono.intersects(p, pt_on_railway):
                total_noise -= (self.remove_leq_10 if tatemono.height<=10 else self.remove_geq_10)
        return total_noise




# railway.csv
wkt_railway = ''
qq_railway = []
with open('railway.csv') as railway_csv:
    railway_spamreader = csv.reader(railway_csv)
    for railway_row in railway_spamreader:
        qq_railway.append(railway_row)

wkt_railway = qq_railway[1][0]


# building_height_wholeArea_FinalinUse.csv -- find height here
buildings_height = []
buildings_id = []
qq_buildings_height = []
with open('building_height_wholeArea_FinalinUse.csv') as buildings_height_csv:
    buildings_height_spamreader = csv.reader(buildings_height_csv)
    for buildings_height_row in buildings_height_spamreader:
        qq_buildings_height.append(buildings_height_row)

for i in range(1, len(qq_buildings_height)):
    if qq_buildings_height[i][12] != '':
        buildings_height.append(float(qq_buildings_height[i][12])/100)
        buildings_id.append(int(qq_buildings_height[i][4]))



# top10bebouwd.csv
qq_buildings = []
with open('top10bebouwd.csv') as buildings_csv:
    buildings_spamreader = csv.reader(buildings_csv)
    for buildings_row in buildings_spamreader:
        qq_buildings.append(buildings_row)

wkt_buildings = []
j = 1
for i in range(0, len(buildings_id)):
    while j<len(qq_buildings) and int(qq_buildings[j][3]) != buildings_id[i]:
        j = j+1
    if j<len(qq_buildings):
        wkt_buildings.append(qq_buildings[j][0])






parser = WKTUnSerializer()
wkt_type_railway, wkt_geom_railway = parser.from_wkt(wkt_railway)


# preprocess
for i in range(len(wkt_geom_railway)):
    p_tuple = wkt_geom_railway[i]
    wkt_geom_railway[i] = Point(p_tuple[0], p_tuple[1])


wkt_geom_buildings = wkt_buildings
for i in range(len(wkt_buildings)):
    wkt_type_buildings, wkt_geom_buildings[i] = parser.from_wkt(wkt_buildings[i])
    wkt_geom_buildings[i] = building(wkt_geom_buildings[i], buildings_height[i])






# read pts
samples = []
with open('Samples.csv') as pts_csv:
    pts_spamreader = csv.reader(pts_csv)
    ii = 0
    for pts_row in pts_spamreader:
        if ii == 0:
            ii += 1
            continue
        samples.append(Point(float(pts_row[0]), float(pts_row[1])))

cal_nn = delft_noise(wkt_geom_railway, wkt_geom_buildings)

sample_noise = []

i = 0
f = open('noise_sample.txt', 'w')
f.close()
for pt in samples:
    nz = cal_nn.cal_noise(pt)
    sample_noise.append(nz)
    f = open('noise_sample.txt', 'a')
    f.write('id: %d, point coordiante: (%1.5f, %1.5f), noise: %f dB\n' % (i, pt.x, pt.y, nz))
    f.close()
    print('id: %d, point coordiante: (%1.5f, %1.5f), noise: %f dB' % (i, pt.x, pt.y, nz))
    i += 1


print(sample_noise)


# cal_nn = delft_noise(wkt_geom_railway, wkt_geom_buildings)
# print(cal_nn.cal_noise(Point(2, 0.5)))



