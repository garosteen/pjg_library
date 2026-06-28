import vsketch
from shapely.geometry import GeometryCollection, Polygon
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

    def __init__(self, numcolors, width=5.0, height=7.0, margin=0.25, blend=False, cm=False):
        self.n = numcolors
        if (cm):
            self.width = width
            self.height = height
            self.margin = margin
        else:
            # Convert inches to cm
            self.width  = 2.54*width
            self.height = 2.54*height
            self.margin = 2.54*margin
        self.centerx = self.width/2.0
        self.centery = self.height/2.0

        self.bound = Polygon([(self.margin, self.margin),
                              (self.width-self.margin,self.margin),
                              (self.width-self.margin,self.height-self.margin),
                              (self.margin,self.height-self.margin)])
        self.layers = []
        for i in range(numcolors):
            self.layers.append([])

    """
    Add the specified geometry to the layer
    If layer is not specified, adds to a random layer.
    """
    def add(self, geom, layer=None):
        if layer is None:
            layer = random.randint(0,self.n-1)
        if geom.geom_type is "GeometryCollection":
            for element in geom.geoms:
                #print(element.geom_type)
                self.add_single_geom(element, layer)
        else:
            self.add_single_geom(geom, layer)

    """
    Only use this after guaranteeing that the geom is simple
    (i.e. not a collection)
    """
    def add_single_geom(self, geom, layer=None):
        if layer is None:
            layer = random.randint(0,self.n-1)
        if (geom.geom_type == "LineString"):
            geom = uf.crop_linestring(self.bound, geom)
        else:
            geom = make_valid(self.bound.intersection(element))
        while layer >= len(self.layers):
            self.layers.append([])

        self.layers[layer].append(geom)

    def draw_to_vsketch(self, vsk: vsketch.Vsketch):
        stroke = 1
        for layer in self.layers:
            vsk.stroke(stroke)
            vsk.geometry(GeometryCollection(layer))
            stroke = stroke+1

    def get(self, layer):
        return GeometryCollection(self.layers[layer])
