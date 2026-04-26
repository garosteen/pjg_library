from shapely.geometry import Polygon, LineString, GeometryCollection
from shapely import affinity

class FramingSquare:

    def __init__(self, geom, center=(0,0)):
        minx, miny, maxx, maxy = geom.bounds

        diffx = (maxx-center[0]) - (center[0]-minx)
        diffy = (maxy-center[1]) - (center[1]-miny)
        offset_factor = 2.0
        width = maxx-minx
        height = maxy-miny
        avg_size = (width+height)/2.0
        w = 2.0

        print(f"minx: {minx}\nmaxx: {maxx}\nminy: {miny}\nmaxy: {maxy}")
        print(f"diffx: {diffx}")
        outer_square = [(minx, miny), 
                        (maxx, miny),
                        (maxx, maxy),
                        (minx, maxy)]
        inner_square = [(minx+w, miny+w),
                        (maxx-w, miny+w),
                        (maxx-w, maxy-w),
                        (minx+w, maxy-w)]

        self.frame = Polygon(outer_square, holes=[inner_square])
        self.xoff = diffx * -offset_factor
        print(self.xoff)
        self.yoff = diffy * -offset_factor
        self.frame = affinity.translate(self.frame, xoff = self.xoff, yoff = self.yoff)
        self.frames = []
        num_frames = 20
        offset = 0.0
        while ((avg_size+offset) > (avg_size*0.6)):
        #for i in range(num_frames):
            offset = offset - 0.05
            square = LineString([(minx-offset, miny-offset),
                            (maxx+offset, miny-offset),
                            (maxx+offset, maxy+offset),
                            (minx-offset, maxy+offset),
                            (minx-offset, miny-offset)])
            self.frames.append(square)

        self.frames = GeometryCollection(self.frames)
        self.frames = affinity.translate(self.frames, xoff = self.xoff, yoff=self.yoff)

