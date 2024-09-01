# Moving Bezier
import random
from vsketch.curves import *
from shapely.geometry import LineString, Point
from shapely import affinity
import bezier
from .bezierUtilities import *

class MovingBezier:
    """A MovingBezier is a system of Bezier curves, in which each of the four points that define a bezier curve are 'moving' across their own paths. 
    Get bezier curve for the system for any timestep from 0.0 to 1.0.
    By default, paths are initialized to random beziers with points within the radius of the bound.
    Set any of the paths to your own LineString if desired.
    """

# TODO: What difference is there from interpolating over a linestring vs evaluating a bezier at t? They must have somewhat different output.

    def __init__(self,bound=10,num_paths=4):
        self.bound = bound # Radius to contain randomly generated values within
        self.paths = []
        for i in range(num_paths):
            self.paths.append(bezier_to_linestring(random_bezier(bound = self.bound)))

    def set_path(self, path: LineString,index=0,):
        self.paths[index] = path

    def get_curve(self,t):
        if t<0.0:
            t = 0.0
        if t > 1.0:
            t = 1.0
        x = []
        y = []
        for p in range(len(self.paths)):
            point = self.paths[p].interpolate(t,normalized=True)
            x.append(point.x)
            y.append(point.y)

        return bezier.Curve.from_nodes([x,y])
