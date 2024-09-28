import numpy as np
import random
from noise import snoise3, snoise2
from pjg_library.IsoLayer import IsoLayer

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
    - set_max / set_min, for customizable max/min values, make the randomize function use these
    - erosion!

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
        self.values = np.array([[(snoise3(x+x_start,y+y_start,warpstrength*snoise2(x*warpsize+x_start,y*warpsize+y_start,octaves=warpoctaves),octaves=octaves)+1.0) / 2.0 for x in x_coords] for y in y_coords])
        neg = False
        min_val = 0.5
        max_val = 0.5
        for row in range(self.rows):
            for col in range(self.cols):
                val = self.values[row][col]
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val
        print(f"Min: {min_val} \nMax: {max_val}")

    def set(self,row,col,val):
        # TODO: check range
        self.values[row][col] = val

    def get(self,row,col):
        # TODO: check range
        return self.values[row][col]

    def get_values(self):
        return self.values

    def get_isolayer(self, value):
        iso = IsoLayer(value)
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                topleft = self.values[row]   [col]
                topright = self.values[row]  [col+1]
                botleft = self.values[row+1] [col]
                botright = self.values[row+1][col+1]

                iso.marching_squares(row, col, topleft, topright, botleft, botright)
        return iso

    def get_topography(self,low=0.0,high=1.0,num_isos=5):
        """
        A more efficient method to get evenly spaced IsoLayers.
        Rather than iterating through all cells for every layer,
        this method iterates through all the cells once.
        """
        isovals = np.linspace(low,high,num_isos+2)
        isos = [IsoLayer(i) for i in isovals[1:-1]]
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                topleft = self.values[row]   [col]
                topright = self.values[row]  [col+1]
                botleft = self.values[row+1] [col]
                botright = self.values[row+1][col+1]
                for iso in isos:
                    iso.marching_squares(row, col, topleft, topright, botleft, botright)

        return isos

    def astar(self,start,end):
        # This should eventually be implemented here
        # May need more parameters? Which directions are allowed, what makes something impassable, etc?
        # What the heuristic is?
        # It should return a sequence of cells.

        pass

