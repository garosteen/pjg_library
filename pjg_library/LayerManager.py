import vsketch
from shapely.geometry import GeometryCollection, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid
from pjg_library import utilityfunctions as uf
import random

"""
Goals of layer manager:
- Add geometries to it to organize into layers
- Set numcolors
- Randomize geometries into available layers
- Configure whether we are blending colors or not
- Get an entire layer as a geometry collection
- Could potentially help with filling things?

What else could the LayerManager do for me?
- Maintain width/height data
- Center coordinates
- Bounds cropping
- Color swatches?

# TODO; random layer doesn't work well if there's only one layer
# TODO: round the edges of the boundary

"""
class LayerManager:

    def __init__(self, numcolors, width=5.0, height=7.0, rows=1, cols=1, margin=0.25, blend=False, cm=False):
        self.cells = []
        self.rows = rows
        self.cols = cols
        self.current_cell = 0

        if (cm):
            self.width = width
            self.height = height
            self.margin = margin
        else:
            # Convert inches to cm
            self.width  = 2.54*width
            self.height = 2.54*height
            self.margin = 2.54*margin

        self.set_cells(self.rows, self.cols)

    def setup(self, vsk: vsketch.Vsketch):
        vsk.size(width=str(self.width)+"cm",height=str(self.height)+"cm",landscape=False,center=False)
        vsk.scale("cm")

    def add(self, geom, layer=None, cell=None):
        if cell is None:
            cell = self.current_cell

        if cell > len(self.cells):
            print(f"Cell {cell} too high in LayerManager.add")
            cell = cell % len(self.cells)
            print(f"New cell number: {cell}")
        self.cells[cell].add(geom, layer)

    def get(self, layer):
        return GeometryCollection(self.layers[layer])

    def draw_to_vsketch(self, vsk: vsketch.Vsketch):
        for cell in self.cells:
            cell.draw_to_vsketch(vsk)

    def set_cell(self, cell):
        self.current_cell = cell % len(self.cells)

    def next(self):
        self.current_cell = (self.current_cell + 1 ) % len(self.cells)

    def set_cells(self, rows=0, cols=0):
        self.cells = []
        self.rows = rows
        self.cols = cols
        self.col_width  =  self.width / self.cols
        self.row_height =  self.height / self.rows
        for row in range(self.rows):
            for col in range(self.cols):
                originx = col * self.col_width
                originy = row * self.row_height
                self.cells.append(LayerManagerCell((originx, originy), (self.col_width, self.row_height), self.margin))

        self.centerx = self.col_width/2.0
        self.centery = self.row_height/2.0

    def get_current_width(self):
        return self.cells[self.current_cell].width

    def get_current_height(self):
        return self.cells[self.current_cell].height

    def get_current_margin(self):
        return self.cells[self.current_cell].margin

    def get_current_center(self):
        w = self.cells[self.current_cell].width
        h = self.cells[self.current_cell].height
        return (w/2.0, h/2.0)


class LayerManagerCell:
    def __init__(self, origin=(0,0), dimensions=(0,0), margin=0.25):
        self.origin = origin
        self.dimensions = dimensions
        self.width = self.dimensions[0]
        self.height = self.dimensions[1]
        self.margin = margin
        self.originx = self.origin[0]
        self.originy = self.origin[1]
        self.centerx = self.width/2.0
        self.centery = self.height/2.0

        self.layers = [[]]

        # TODO: radius for edges?
        self.bound = Polygon([(self.margin, self.margin),
                              (self.width-self.margin,self.margin),
                              (self.width-self.margin,self.height-self.margin),
                              (self.margin,self.height-self.margin)])

    """
    Add the specified geometry to the layer
    If layer is not specified, adds to a random layer.
    """
    def add(self, geom, layer=None):
        if not (isinstance(geom, BaseGeometry)):
            # Not a Shapely BaseGeometry, assume it's an iterable list of geometries
            l = layer
            for i, g in enumerate(geom):
                if layer is None:
                    l = i
                self.add(g, l)
            return

        if geom.geom_type == "GeometryCollection":
            for element in geom.geoms:
                self.add(element, layer)
        if layer is None:
            layer = random.randint(0,len(self.layers)-1)
        if (geom.geom_type == "LineString"):
            geom = uf.crop_linestring(self.bound, geom)
        else:
            geom = make_valid(self.bound.intersection(geom))
        while layer >= len(self.layers):
            self.layers.append([])

        self.layers[layer].append(geom)

    def draw_to_vsketch(self, vsk: vsketch.Vsketch):
        vsk.pushMatrix()
        vsk.translate(self.originx, self.originy)
        stroke = 1
        for layer in self.layers:
            vsk.stroke(stroke)
            vsk.geometry(GeometryCollection(layer))
            stroke = stroke+1
        vsk.popMatrix()

