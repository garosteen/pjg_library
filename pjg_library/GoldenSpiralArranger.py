from shapely import affinity
from shapely.geometry import Point, GeometryCollection
import math
import random

class GoldenSpiralArranger:
    def __init__(self, center=(0,0)):
        self.arrangement = GeometryCollection(Point(center))
        self.angle_increment = 2.39996 # Allegedly the "golden angle"
        self.angle = random.random()*2*math.pi # Randomize start angle
        self.center = center

    def place(self, geom):
        # for now, trust that the geom is centered
        # TODO; make sure the geom is centered to begin with
        self.angle = self.angle + self.angle_increment
        r = 0.0
        r_inc = 0.5
        xoff = 0.0
        yoff = 0.0
        translated = affinity.translate(geom, xoff=xoff, yoff=yoff)

        while translated.intersects(self.arrangement):
            r = r + r_inc
            print(r)
            xoff = math.cos(self.angle)*r
            yoff = math.sin(self.angle)*r 
            translated = affinity.translate(geom, xoff=xoff, yoff=yoff)

        # It no longer intersects
        self.arrangement = GeometryCollection([self.arrangement, translated])
        return (xoff, yoff)



