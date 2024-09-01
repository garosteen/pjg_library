import math
import random
from shapely.geometry import LineString, Point
# Idea - this could be a 'star' generator instead of spirographing
# TODO: some sort of 'path' object?

class Spirograph:
    '''Object that can be queried to get coordinates at specified step'''

    def __init__(self, center=(0,0), radius=1.0):
        n = random.randint(22,179) # Arbitrarily limiting it so it's not SO small sometimes
        self.inner_r = n/180.0
        print(self.inner_r)
        self.marker_r = random.random()*1.5 # Percentage of smaller circle
        self.set_angle(0)
        self.center = center
        self.radius = radius

    def set_angle(self, angle):
        self.angle = angle
        self.set_inner_center()
        self.set_marker()

    def set_inner_center(self):
        '''Set the location of the center of the inner circle'''
        self.center_angle = self.angle
        self.center_d = 1.0-self.inner_r
        self.inner_center = (math.cos(self.center_angle)*(self.center_d),math.sin(self.center_angle)*(self.center_d))

    def set_marker(self):
        l = self.angle
        r = self.inner_r
        theta = l/r # This is how much the inner circle rotates from the length alone
        theta += self.angle
        self.theta = theta # Rotation of inner circle

        edge = (math.cos(theta)*(r*self.marker_r),math.sin(theta)*(r*self.marker_r))
        pos = (self.inner_center[0]+edge[0],self.inner_center[1]+edge[1])
        self.marker_theta = math.atan2(pos[1],pos[0]) # Angle from center to location of marker
        self.marker_d = math.dist(pos,(0,0)) # Distance from center to location of marker

    def get_xy(self):
        '''Return x,y coordinates based on center and radius'''

        x = self.radius * self.marker_d * math.cos(self.marker_theta) + self.center[0]
        y = self.radius * self.marker_d * math.sin(self.marker_theta) + self.center[1]
        return (x,y)

    def get_coordinates(self):
        return (self.marker_theta,self.marker_d)
        
    def get_inner_center_xy(self):
        x = self.radius * self.center_d * math.cos(self.center_angle) + self.center[0]
        y = self.radius * self.center_d * math.sin(self.center_angle) + self.center[1]
        return (x,y)

    def get_center(self):
        # TODO: What even is this method? We need an actual get center, right?
        return self.center
        #return (self.center_angle,self.center_d)

    def coordinates(self, angle):
        '''Return a tuple (angle, radius) where radius is a fraction of max radius'''
        # The basic idea of a spirograph is that a circle is rolling inside another circle.
        # Let's just focus on this two-circle spirograph for now.

        # At a given angle, how much has the inner circle rotated?
        # Length of arc is = to angle in radians
        l = angle
        r = self.inner_r
        theta = l/r # This is how much the inner circle rotates from the length alone
        # But we must ADD the rotation from the curve of the outer circle
        theta += angle
        # theta is the amount of rotation the inner circle has performed
        # Center of inner circle should be at radius = 1.0-r
        inner_center = (math.cos(angle)*(1.0-r),math.sin(angle)*(1.0-r))
        edge = (math.cos(theta)*(r*self.marker_r),math.sin(theta)*(r*self.marker_r))
        pos = (inner_center[0]+edge[0],inner_center[1]+edge[1])
        # Get from these x,y coordinates to angle,radius?
        pos_angle = math.atan2(pos[1],pos[0]) # Does this work?
        pos_radius = math.dist(pos,(0,0))

        return (pos_angle, pos_radius)

    def get_path(self, step):
        '''Return a list of tuples representing all coordinates every step'''
        pass
    def get_linestring(self,rotations=8,step=1):
        coords = []
        self.set_angle(0)
        for theta in range(0,int(360*rotations),step):
            self.set_angle(math.radians(theta))
            coords.append(self.get_xy())
        return LineString(coords)
