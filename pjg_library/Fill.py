from shapely.geometry import LinearRing,LineString, Point,Polygon, GeometryCollection, MultiLineString
import math
import numpy as np
from pjg_library import utilityfunctions as uf
import random

class Fill:
    """
    Goal of this class is to provide different Fill methods.
    What is the standard format for a fill method?
    Input:
        Polygon (or geometry?)
        Density
    Output:
        GeometryCollection?
        Collections of coordinates?
        How reliant should I be on shapely?

    Standard output for non-fillable shapes should be None
    3. Returns a GeometryCollection
    If the Polygon 'closes in' and has a gap in where it is fillable, we get jumping fill lines.
    Need to detect when they are too far apart to add together

    TODO:
    - Need to be able to fill disparate geometries.
        - Detect if it's a collection, and do it for every one?
    - Don't connect lines if the connection crosses the polygon
    - Could Fill take an enum, or have a setting for a default fill?
        - Would need to have specific settings for different fills, so you can control them without passing them as arguments. For instance, "radiant" would need to be a variable that you can set, so when you set it to radial fill, you can still control the radiant point from the Fill object.

    """
    def __init__(self, stroke_width=0.05, density=1.0):
        self.stroke_width = stroke_width
        self.density = density

    def radial_fill(self, poly: Polygon, density=None, radiant=Point(0.0,0.0)) -> GeometryCollection:
        # TODO: Sometimes a poly just doesn't get filled. Why?
        # TODO: debug moving the radiant, when the line gets split in two, it's not working well
        # How should that even work?
        # Need to split the portions into clusters based on where they are -- can I count on reverse/not reverse as a guide for which ones would go with which? Do I need to measure distance of their starting points, or compare them some other way?
        if (density == None):
            density = self.density

        # Buffer the polygon to make it slightly smaller, by the stroke width
        poly = poly.buffer(-self.stroke_width/2.0, join_style=2, mitre_limit=10.0)
        if poly.is_empty:
            return GeometryCollection()
        #min_r=self.stroke_width/2.0
        min_r=self.stroke_width
        max_r=0.0

        # Find minimum and maximum radius 
        # Okay, the naive method is just start from the radiant, increase a circle gradually, and keep checking if the circle contains the poly.
        # TODO: find out how expensive this method is, and if there's a better way
        # TODO: are there maybe built-in methods for Shapely geoms?
        # Some other idea might be to get the bounds of the geometry, and just get max/min radius from that? The radius isn't very important, because it doesn't have to be precise. It just needs to be bigger than the actual geometry.
        r = 1.0
        while (max_r == 0.0):
            c = radiant.buffer(r) # Create a circle at the radiant
            if (c.contains(poly)):
                # Once the circle is large enough that the poly is fully contained, this is a max_r
                max_r = r
            if poly.disjoint(c):
                # If the circle and the polygon to not intersect or contain each other, this is a safe min_r
                min_r = r
            r = r + 1.0

        #print(f"max_r: {max_r}\nmin_r: {min_r}")

        # given max_r, find angle for given arclength
        theta_step = self.stroke_width/max_r/density # Using the widest point to decide how dense to fill
        min_theta, max_theta = uf.get_bounding_angles(radiant, poly)
        clusters = []
        lines = []
        reverse = False
        for theta in np.arange(min_theta, max_theta, theta_step):
            ct = math.cos(theta)
            st = math.sin(theta)
            close = [ct*min_r+radiant.x, st*min_r+radiant.y]
            far =   [ct*max_r+radiant.x, st*max_r+radiant.y]
            start = close
            end = far
            if (reverse):
                start = far
                end = close
            intersection = LineString([start, end]).intersection(poly)

            if (intersection.is_empty):
                # We are on a break. Is it a new break?
                if len(lines) != 0:
                    # It's a new break
                    connected = LineString([coord for line in lines for coord in line.coords]) # nested list comprehensions are a mindfuck
                    clusters.append(connected)
                    lines = []

            if not(intersection.is_empty):
                if intersection.geom_type != "LineString" and intersection.geom_type != "Point":
                    for geom in intersection.geoms:
                        if geom.geom_type == "LineString":
                            lines.append(geom)
                elif intersection.geom_type == "LineString":
                    lines.append(intersection)
            reverse = not(reverse)

        # Check if there's another cluster
        if len(lines) != 0:
            # There was a straggler
            connected = LineString([coord for line in lines for coord in line.coords]) # nested list comprehensions are a mindfuck
            clusters.append(connected)

        #lines_collection = GeometryCollection(lines)
        #if lines_collection.geom_type == 'GeometryCollection' and len(lines_collection.geoms) > 1:
        #    connected = LineString([coord for line in lines_collection.geoms for coord in line.coords])
        #    return GeometryCollection([connected,poly])

        #return GeometryCollection([lines_collection,poly])
        clusters.append(poly)
        return GeometryCollection(clusters)


# TODO: A fill function that takes the geometry and creates a boolean grid at a certain scale, randomly toggles cells corresponding to density, then uses the grid path for QR codes to create the fill.


# Touches all grid cells, with backtracking, minimizing number of paths
# 
def explore_grid_from_cell(grid, row=0, col=0):
    """
    Takes a boolean array and a starting row and column
    Returns a path that explores all possible True locations from that starting point,
    where it can access all 8 surrounding cells from a given cell.
    The path is not optimal, and backtracks in order to access any cells that have not yet been reached.
    """
    # TODO: set whether the directions are randomized or not
    # TODO: It would be cool for the directions to be randomized ONCE, so that the general priorities can be randomized, but then it stays the same for the whole operation
    # TODO: Is there a way to do this same thing WITHOUT recursion?
    if row < 0 or col < 0:
        return None, None
    rows = len(grid)
    cols = len(grid[0])
    if row >= rows or col >= cols:
        return None, None
    
    if not grid[row][col]:
        return None, None

    # Toggle the cell
    grid[row][col] = False
    # Start a path
    path = [(col,row)]
    backtrack = [(col,row)]
    directions = [
        (row, col+1),
        (row+1, col),
        (row, col-1),
        (row-1, col),
        (row+1, col+1),
        (row+1, col-1),
        (row-1, col-1),
        (row-1, col+1)]
    random.shuffle(directions)

    directions = [explore_grid_from_cell(grid, d[0], d[1]) for d in directions]
    
    previous = None
    backtrack_addition = None
    for direction in directions:
        if direction[0]:
            if previous is not None:
                path = path + previous[::-1] + [(col,row)]
            previous = direction[1]
            path = path + direction[0]
            backtrack_addition = direction[1]

    if (backtrack_addition is not None):
        backtrack = backtrack + backtrack_addition

    return path, backtrack



    # If I add a path, and then need to add another path, I need to re-add the previous path but reversed.
    # instead of naming them, I could throw them in an array
    
    # Okay, so, path traversal:
    # Need to build a path and modify the matrix
    # Do I allow backtracking? That's what I want. So let's build it in.
    # 
    # From the current cell, check right, down, left, up
    # First one that is available, 

    # One problem: how do I differentiate between just checking/following the one path, versus getting multiple paths?
    # For the recursion to work well, the function needs to return just one path.
    # Should the collection of paths be a different function?



