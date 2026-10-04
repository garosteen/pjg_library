from shapely.geometry import LineString, Polygon, Point, GeometryCollection
import random
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
    I feel like I should be able to give the swatch a width and height and x and y, and have it use those coordinates
    Should I give swatch a layermanager? 
    It doesn't make sense for this to be a "swatch" object, I mostly need every method to be independent.
    So I shouldn't be returning the self.layers, and self shouldn't even *have* a layers section

    Should Swatch have x, y, w, h at all?
    It's potentially a convenience, so I don't have to keep passing around the values when I'm calling other functions.
    If so, should the individual functions set those values when they receive them?
    Maybe the simplest thing is to get rid of it.
"""

"""
Do some stuff here
Be myself!
"""


class Swatch:
    def __init__(self, numColors: int, x, y, width, height):
        # TODO: Swatch should have the pen width
        self.numColors = numColors
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.set_grid_size(rows = self.numColors, cols = self.numColors)
        self.layers = [[] for color in range(numColors)]
        self.fill = Fill.Fill()
        self.geometryCollection = GeometryCollection()
        # TODO: REALLY need to stop relying on this radiant thing. Swatch line needs to be more generic!
        self.radiant_offset = 1.5

    def set_grid_size(self, rows, cols):
        self.col_width = self.width / cols
        self.row_height = self.height / rows

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

    Could I generalize this like crazy? Give it a function for what to draw at each square?
    Then I could use this for LOTS of things. Nested circles, for instance.

    The action function for swatch_line should take:
        - location: x,y
        - dimension/scale; w, h
        - density

    """
    def swatch_line(self, x, y, w, h, layer, rows, cols, row, col, rowstep, colstep, steps, start_density, end_density, fill_function):
        # TODO: name this more accurately? It's a single layer sequence of swatches
        # TODO: pass it the function to draw to each thing?
        swatches = []
        col_w = w / cols
        row_h = h / rows
        # TODO: gap? Or would this be handled by the drawing function?
        for step in range(steps):
            # TODO: do I really need a conditional here? That seems crazy, surely I can calculate density in one go
            if steps > 1:
                density = start_density + (step/(steps-1)) * (end_density - start_density)
            else:
                density = start_density
            cur_row = row + step*rowstep
            cur_col = col + step*colstep
            cur_x = x + (cur_col * (col_w))
            cur_y = y + (cur_row * (row_h))
            #box = [[cur_x, cur_y],
            #       [cur_x+col_w,cur_y],
            #       [cur_x+col_w,cur_y+row_h],
            #       [cur_x,cur_y+row_h]]
            #poly = Polygon(box)
            # TODO: this fill should be adjustable to different fill methods
            #radiant = Point(cur_x + (col_w/2.0) + self.radiant_offset, 
            #                cur_y + (row_h/2.0) + self.radiant_offset) 
            #f = self.fill.radial_fill(poly, radiant=radiant, density=density)
            f = fill_function(cur_x, cur_y, col_w, row_h, density)
            swatches.append(f)
        return swatches

    def get_radiant_fill_function(self, radiant_offset):
        def radiant_fill(x, y, w, h, density):
            box = [[x, y],
                   [x+w, y],
                   [x+w, y+h],
                   [x, y+h]]
            poly = Polygon(box)
            radiant = Point(x + w/2.0 + radiant_offset,
                            y + h/2.0 + radiant_offset)
            f = self.fill.radial_fill(poly, radiant=radiant, density=density)
            return f
        return radiant_fill

    def get_line_fill_function(self, angle):
        def line_fill(x, y, w, h, density):
            # TODO: should I have functions that generalize this behavior?
            # Like, a shapes class that I can give the x,y,w,h, and get my polygon back? 
            # Probably this kind of shit already exists. Should I do more looking?
            box = [[x, y],
                   [x+w, y],
                   [x+w, y+h],
                   [x, y+h]]
            poly = Polygon(box).buffer(-0.05)
            f = self.fill.line_fill(poly, density, angle=angle)
            return f
        return line_fill

    def vertical_swatch(self, x, y, w, h):
        max_density = 1.5
        min_density = 0.3
        density_steps = 3
        layers = [[] for c in range(self.numColors)]
        for i in range(self.numColors):
            layer = i
            line = self.swatch_line(x, y, w, h, layer, 
                                    rows=self.numColors, 
                                    cols=self.numColors, 
                                    row=i, 
                                    col=0, 
                                    rowstep=0.5, 
                                    colstep=1, 
                                    steps=4, 
                                    start_density=1.5, 
                                    end_density=0.3)
            layers[layer].append(line)

            layer = (i+1)%self.numColors
            line = self.swatch_line(x, y, w, h, layer, 
                                    rows=self.numColors, 
                                    cols=self.numColors, 
                                    row=i+1, 
                                    col=4, 
                                    rowstep=-0.5, 
                                    colstep=-1, 
                                    steps=4, 
                                    start_density=1.5, 
                                    end_density=0.3)
            layers[layer].append(line)

        return layers
        
    def triangle_blend(self, x, y, w, h):
        density = 0.6 # 0.7 is too much for the fountain pens, not enough showing through.
        layers = [[] for c in range(self.numColors)]
        for c in range(self.numColors):
            print(c)
            radiant_offset = (w / self.numColors) * 1.25
            fill_function = self.get_radiant_fill_function(radiant_offset)
            swatches = self.swatch_line(x, y, w, h, c, self.numColors, self.numColors,
                                        self.numColors-c-1, 0, -0, 1, self.numColors-c, density, density, fill_function)
            layers[c].append(swatches)

            radiant_offset = radiant_offset*-1
            fill_function = self.get_radiant_fill_function(radiant_offset)
            swatches = self.swatch_line(x, y, w, h, c, 
                                        rows=self.numColors, 
                                        cols=self.numColors,
                                        row=self.numColors-c-1, 
                                        col=0, 
                                        rowstep=1, 
                                        colstep=1, 
                                        steps=c+1, 
                                        start_density=density, 
                                        end_density=density, 
                                        fill_function=fill_function)
            layers[c].append(swatches)
        print(len(layers))
        return layers

    def barcode(self, x, y, w, h):
        # TODO: should be able to decide whether this is vertical or horizontal
        layers = [[] for c in range(self.numColors)]
        y_start = y
        layer = 0
        pen = 0.025
        while (x < w):
            y = y_start
            layer = random.randint(0,self.numColors-1)
            num_lines = random.randint(1,10)
            coords = []
            direction = 1
            current_line = 0
            while (current_line < num_lines and x < w):
                coords.append((x, y))
                y = y + (h * direction)
                coords.append((x, y))
                x = x + pen
                direction = direction * -1
                current_line += 1
            line = LineString(coords)
            layers[layer].append(line) 
        return layers

    def crosshatch(self, x, y, w, h, steps):
        layers = [[] for c in range(self.numColors)]
        d_theta = 180/steps
        angle = 0
        for layer in range(self.numColors):
            for step in range(steps):
                angle = step*d_theta
                fill_function = self.get_line_fill_function(angle=angle)
                swatch = self.swatch_line(x,y,w,h,
                                 layer=1,
                                          rows=self.numColors,
                                          cols=steps,
                                 row=layer,
                                 col=step,
                                 rowstep=0,
                                 colstep=1,
                                 steps=steps-step,
                                 start_density=1.0,
                                 end_density=1.0,
                                 fill_function = fill_function)
                layers[layer].append(swatch)

        return layers
