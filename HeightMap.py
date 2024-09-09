import numpy as np
import random
from noise import *

class HeightMap:
    """
    A HeightMap is essentially an array of values with some convenience utilities built in.
    It is intended to represent elevation or texture in a given area.
    Values are assumed to be in range 0.0-1.0
    - Convenient auto-generation of random perlin noise
    - Set cutoff points
    - Get slope angles and such
    TODO:
    - A shading function
        - Give it an angle 0-2PI for which slopes need to be shaded
        - The best thing to do might be to make a new HeightMap, populate it with 0/1 depending on if the slope at that point is within tolerance for being shaded, then create an IsoLayer to define the areas that are shaded. Probably would need the map to be bigger by 1 in every direction so that the isolines connect as needed on the edges.
    """
    def __init__(self,rows,cols=0):
        """
        If only one argument is given, the constructor creates a square HeightMap.
        Values are initialized to 0.5.
        """
        self.rows = rows
        self.cols = rows
        if cols != 0:
            self.cols = cols
        self.values = [[0.5 for c in range(cols)] for r in range(rows)]
    
    def randomize(self,x_range=0,y_range=0,octaves=2,warpstrength=1.0,warpsize=0.5,warpoctaves=2):
        if x_range == 0:
            x_range = self.cols/10.0
        if y_range == 0:
            y_range = self.rows/10.0

        x_coords = np.linspace(0., x_range, self.cols) # Indexing perlin x vals from 0-x_range, for x_num points
        y_coords = np.linspace(0., y_range, self.rows) # Indexing y vals from 0-10, for y_num points
        x_start = random.random()*10000
        y_start = random.random()*10000
        self.values = np.array([[snoise3(x+x_start,y+y_start,warpstrength*snoise2(x*warpsize+x_start,y*warpsize+y_start,octaves=warpoctaves),octaves=octaves) for x in x_coords] for y in y_coords])

    def set(self,row,col,val):
        self.values[row][col] = val

    def get(self,row,col):
        return self.values[row][col]

    def get_values(self):
        return self.values

    def get_isolayer(self, value):
        # TODO: The core topography functionality should be here, so I can query it at specific values
        pass

    def get_topography(self,low=0.0,high=1.0,layers=5):
        # TODO: this should just iterate over the values and call get_isolayer for each one and compile them together.
        isovals = np.linspace(low,high,layers)
        print(isovals)
        isos = [IsoLayer(i) for i in isovals]
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                topleft = self.values[row]   [col]
                topright = self.values[row]  [col+1]
                botright = self.values[row+1][col+1]
                botleft = self.values[row+1] [col]

                # These vectors are just relative to the row/col coordinates -- they aren't absolute at all, it's up to the display to scale them I think.
                top_interp = 0.5
                bot_interp = 0.5
                right_interp = 0.5
                left_interp = 0.5

                for index, val in enumerate(isovals):
                    iso = isos[index]
                    flags = 0
                    if topleft > val:
                        flags += 1
                    if topright > val:
                        flags += 2
                    if botright > val:
                        flags += 4
                    if botleft > val:
                        flags += 8

                    # No interp yet, just get some basics going
                    if flags == 0 or flags == 15:
                        continue
                    else:
                        if topright != topleft:
                            top_interp = abs(val-topleft) / abs(topright-topleft)
                        if botright != botleft:
                            bot_interp = abs(val-botleft) / abs(botright-botleft)
                        if topright != botright:
                            right_interp = abs(val-topright) / abs(botright-topright)
                        if topleft != botleft:
                            left_interp = abs(val-topleft) / abs(botleft-topleft)

                    top = (col+top_interp,row)
                    right = (col+1.0,row+right_interp)
                    bottom = (col+bot_interp,row+1.0)
                    left = (col,row+left_interp)

                    if flags == 1 or flags == 14:
                        iso.add(left,top)
                    elif flags == 2 or flags == 13:
                        iso.add(top,right)
                    elif flags == 3 or flags == 12:
                        iso.add(left,right)
                    elif flags == 4 or flags == 11:
                        iso.add(right,bottom)
                    elif flags == 5:
                        iso.add(top,right)
                        iso.add(left,bottom)
                    elif flags == 6 or flags == 9:
                        iso.add(top,bottom)
                    elif flags == 7 or flags == 8:
                        iso.add(left,bottom)
                    elif flags == 10:
                        iso.add(left,top)
                        iso.add(bottom,right)
        return isos

    def astar(self,start,end):
        # This should eventually be implemented here
        # May need more parameters? Which directions are allowed, what makes something impassable, etc?
        # What the heuristic is?
        # It should return a sequence of cells.

        pass

class IsoLayer:
    """
    An Isolayer represents a collection of contour curves for a specific value.
    """

    def __init__(self,value):
        self.value = value
        self.curves = []

    def add(self,start,end):
        # Check if line is compatible with any others
        curve = Curve(start,end)
        #self.curves.append(curve)
        #return
        match_1 = -1
        match_2 = -1
        for index,other in enumerate(self.curves):
            compat = curve.get_compatibility(other)
            if compat != 0:
                if match_1 == -1:
                    match_1 = index
                else:
                    match_2 = index
        
        if match_1 == -1:
            # No match, just add the curve
            self.curves.append(curve)
        else:
            self.curves[match_1].add(curve)
            if match_2 != -1:
                self.curves[match_2].add(self.curves[match_1])
                self.curves.pop(match_1)

    def get_curves(self):
        return self.curves

class Curve:
    """
    A Curve is a sequence of points.
    This should probably be called a Path instead of a Curve, since it doesn't actually
have any curvature-related functionality.
    """
    def __init__(self,start,end):
        self.points = [start,end]
        self.tolerance = 0.01

    def get_start(self):
        return self.points[0]

    def get_end(self):
        return self.points[-1]

    def add(self,other):
        compatible = self.get_compatibility(other)

        if compatible == 0:
            # Curves are not compatible.
            return 0
        if compatible == 1:
            # start and other end are the same. Put other at the start, without its end
            # Append self.points to other.points without its end
            self.points = other.points[:-1] + self.points
            #self.points = other.points + self.points

        elif compatible == 2:
            # end and other start are the same. Place other at the end, without its start
            self.points = self.points + other.points[1:]

        elif compatible == 3:
            # same start points, reverse the other, don't include its start, and add to self
            #self.points = other.points[-1:0:-1] + self.points
            self.points = other.points[:0:-1] + self.points

        elif compatible == 4:
            # same end points, reverse the other, don't include its end, add to self
            #self.points = self.points + other.points[-2:-1:-1]
            self.points = self.points + other.points[-2::-1]


    def get_compatibility(self,other):
        """
        Checks whether two curves can be combined into one curve. Return code indicates
        how the curves can be combined:
        0: Not compatible
        1: self.start == other.end
        2: self.end   == other.start
        3: self.start == other.start
        4: self.end   == other.end
        """
        start = self.get_start()
        end = self.get_end()
        other_start = other.get_start()
        other_end = other.get_end()

        start_diff_x = abs(start[0] - other_start[0])
        start_diff_y = abs(start[1] - other_start[1])
        end_diff_x = abs(end[0] - other_end[0])
        end_diff_y = abs(end[1] - other_end[1])

        start_end_diff_x = abs(start[0] - other_end[0])
        start_end_diff_y = abs(start[1] - other_end[1])

        end_start_diff_x = abs(end[0] - other_start[0])
        end_start_diff_y = abs(end[1] - other_start[1])

        if start_end_diff_x < self.tolerance and start_end_diff_y < self.tolerance:
            # start and other end are the same. 
            return 1
        elif end_start_diff_x < self.tolerance and end_start_diff_y < self.tolerance:
            # end and other start are the same.
            return 2
        elif start_diff_x < self.tolerance and start_diff_y < self.tolerance:
            # same start points
            return 3
        elif end_diff_x < self.tolerance and end_diff_y < self.tolerance:
            # same end points
            return 4
        else:
            return 0



