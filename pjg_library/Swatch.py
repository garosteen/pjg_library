from shapely.geometry import LineString, Polygon, Point, GeometryCollection
from pjg_library import Fill
"""
Goals of this class:
    Embed a stylish little color test / color swatch in a corner of my other sketches
    How do I imagine this working?
    Do I need to create a swatch object, or just ask for things on the fly?
    swatch = Swatch.createGrid(4)
    What does the swatch need to know?
    - Number of colors
    - Available space/size/coordinates?
        - Or, should it just create with whatever space it needs, and I have to place it correctly on the other end?
        - Because, what if I don't know how much space it needs? I shouldn't have to figure that out.
        - So let's say that it just creates generically, starting from 0, and makes it as big as it needs to be
    What do I get from the swatch?
        - A layer for every color
        - Height and width
        - 

    TODO:
    Need a standard straightline fill method
"""

"""
Do some stuff here
Be myself!
"""


class Swatch:
    gap = 0.5 # grid units
    def __init__(self, numColors: int, gridSize = 0.5, xoff=0.0, yoff=0.0):
        self.numColors = numColors
        self.layers = [[] for color in range(numColors)]
        self.fill = Fill.Fill()
        self.geometryCollection = GeometryCollection()
        self.gridSize = gridSize
        self.radiant_offset = -self.gridSize
        self.xoff = xoff
        self.yoff = yoff
        # So, the problem is that I don't know what yoff is going to be until I create the swatch.
        # Should I have a direction that the swatch builds in? So that I can say yoff is paperheight - 1, and then the swatches go negative from there, instead of positive?
        # Should I just have a set xoff and set yoff method? Translates it for me?
        # I could have a "recalibrate for height and width" method?
        # 

    def get_bounds(self):
        return self.geometryCollection.bounds

    def get_bound_geometry(self):
        minx, miny, maxx, maxy = self.get_bounds()
        return Polygon([(minx, miny),
                        (maxx, miny),
                        (maxx, maxy),
                        (minx, maxy),
                        (minx, miny)])

    """
    swatch_line creates a sequence of swatches, starting from (row, col) and moving (rowstep, colstep) for steps,
    from start_density to end_density.
    """
    def swatch_line(self, layer, row, col, rowstep, colstep, steps, start_density, end_density):
        g = self.gridSize
        gap = self.gap * self.gridSize
        for step in range(steps):
            if steps > 1:
                density = start_density + (step/(steps-1)) * (end_density - start_density)
            else:
                density = start_density
            cur_row = row + step*rowstep
            cur_col = col + step*colstep
            x = cur_col * (g+gap)
            y = cur_row * (g+gap)
            box = [[self.xoff+x,  self.yoff+y-g],
                   [self.xoff+x+g,self.yoff+y-g],
                   [self.xoff+x+g,self.yoff+y],
                   [self.xoff+x  ,self.yoff+y]]
            poly = Polygon(box)
            # TODO: this fill should be adjustable to different fill methods
            f = self.fill.radial_fill(poly, radiant=Point(self.xoff+x+self.radiant_offset, self.yoff+y+self.radiant_offset), density=density)
            self.layers[layer].append(f)
            self.geometryCollection = GeometryCollection([self.geometryCollection, f])


    def vertical_swatch(self):
        g = self.gridSize
        max_density = 1.5
        min_density = 0.3
        density_steps = 3
        for i in range(self.numColors):
            self.swatch_line(i, i, 0, 0.5, 1, 4, 1.5, 0.3)
            self.swatch_line((i+1)%self.numColors, i+1, 4, -0.5, -1, 4, 1.5, 0.3)

        return self.layers
        
    def triangle_blend(self):
        density = 0.6 # 0.7 is too much for the fountain pens, not enough showing through.
        for c in range(self.numColors):
            self.radiant_offset = -self.gridSize
            self.swatch_line(c, -c, 0, -0, 1, self.numColors-c, density, density)
            self.radiant_offset = 2*self.gridSize
            self.swatch_line(c, -c, 0, 1, 1, c+1, density, density)
        return self.layers

