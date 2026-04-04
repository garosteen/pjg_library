from shapely.geometry import LineString,MultiLineString, LinearRing, Polygon, Point
import numpy as np
import math

def cm(n):
    return str(n)+'cm'

def mm(n):
    #return n * 3.543307
    return str(n)+'mm'

def in_to_cm(n):
    return n*2.54

def crop_linestring(bound,ls):
    """Get the intersection LineString without slicing at self-intersections
    When you use the shapely intersection method to crop a linestring so it fits within a polygon,
    Shapely also cuts the LineString at all of its self-intersections. Obviously this creates problems 
    for plotting, when the loops of a line are drawn separately. This has been a problem for a handful of 
    other people, but I couldn't find a solution other than "do it yourself".

    The goal of this function is to do the intersection without cutting the line to pieces.
    https://stackoverflow.com/questions/35760810/how-to-preserve-a-complex-line-during-shapely-intersection
    https://gis.stackexchange.com/questions/403121/python-shapely-crop-clip-using-intersection-cropped-line-is-split-at-self-i
    """
    segments = [LineString(x).intersection(bound) for x in zip(ls.coords, ls.coords[1:])]
    lines = [] # Output
    line = [] # Building zone for the linestring
    
    for segment in segments:
        if len(segment.coords) == 0:
            if len(line) > 0:
                lines.append(LineString(line))
            line = []
        else:
            if len(line) == 0:
                line.append(segment.coords[0])

            if line[-1] != segment.coords[0]:
                print('broken segment')
                lines.append(LineString(line))
                line = []
                line.append(segment.coords[0])

            line.append(segment.coords[1])


    if len(line) > 0:
        lines.append(LineString(line))

    return MultiLineString(lines)

# TODO: rename to something like polar_to_xy
def getxy(startx,starty,radius,theta):
    """Get an x,y tuple based on starting coordinate, distance, and angle"""
    x = startx + np.cos(theta)*radius
    y = starty + np.sin(theta)*radius
    return (x,y)

def get_all_coords(geom):
    """Given any geometry, return an array of all of its coordinates."""
    coords = []
    if isinstance(geom, (Point, LineString, LinearRing)):
        coords.extend(list(geom.coords))
    elif isinstance(geom, Polygon):
        coords.extend(list(geom.exterior.coords))
        # There's a duplicate point in exterior/interior, but I don't think that's a problem.
        for interior in geom.interiors:
            coords.extend(list(interior.coords))
    elif hasattr(geom, 'geoms'):
        for sub_geom in geom.geoms:
            coords.extend(get_all_coords(sub_geom))

    return coords

def get_bounding_angles(center, geom):
    # Go through every point in the polygon, get angle.
    min_theta = 2 * math.pi
    max_theta = 0.0

    coords = get_all_coords(geom)
    # TODO: if center is WITHIN geom, return
    if geom.contains(center):
        return(0.0, 2 * math.pi)

    for p in coords:
        
        theta = math.atan2(p[1] - center.y, p[0] - center.x)
        if (theta < 0.0):
            theta += 2 * math.pi
        if (theta < min_theta):
            min_theta = theta
        if (theta > max_theta):
            max_theta = theta

    #print(f"{min_theta}, {max_theta}")
    return (min_theta,max_theta)

def upscale(grid, level=2):
    # Doubles the size of a 2d array
    # copy each cell to right, bottom-right, and bottom
    return [[grid[row//level][col//level] for col in range(len(grid[0]*level))] for row in range(len(grid)*level)]

class Grid:
    """Convenience class to make it easier to subdivide space into a grid.
    Takes a center tuple, dim tuple (width and height), rows, and cols."""
    def __init__(self,center,dim,rows,cols):
        self.dim = dim
        self.center = center
        self.topleft = (self.center[0]-(self.dim[0]/2.0),
                        self.center[1]-(self.dim[1]/2.0))
        self.rows = rows
        self.cols = cols
        self.cell_dim = (self.dim[0]/(cols),self.dim[1]/(rows))
        self.centers = []
        for row in range(rows):
            for col in range(cols):
                x = self.topleft[0]+self.cell_dim[0]/2.0+(self.cell_dim[0]*col)
                y = self.topleft[1]+self.cell_dim[1]/2.0+(self.cell_dim[1]*row)
                self.centers.append((x,y))

    def get(self,row,col):
        return self.centers[(row*self.cols)+col]
