from shapely.geometry import Polygon,GeometryCollection
from .SegmentDisplay import *
import datetime
"""
Goals of border class:
- Give it dimensions, random seed
- Get border and seed/name separately
- Border should be an object that I can use to crop the sketch
TODO:
- Set "name", so the boundary can be flexible if I want to write something else besides my name
- Some way to add text to the border, so I can choose to display parameters or something.
You give the SketchBorder your paper size or final paper size, and it will create a border 
that is a buffer length away from the edge.
You can call get_frame to get a Polygon representing the actual paper size, for cutting a larger
piece down to size.

"""

class SketchBorder:
    def __init__(self,width,height,seed=0,buffer=1.0):
        self.width = width
        self.height = height
        self.seed = seed
        self.buffer = buffer 

        self.top = 0 - self.height/2.0 + self.buffer
        self.bottom = self.height/2.0 - self.buffer
        self.left = 0 - self.width/2.0 + self.buffer
        self.right = self.width/2.0 - self.buffer

        self.charheight = 0.5

# What would the display coordinates look like if they were simple?
# Set x,y then tell it to align according to the bottom?
        self.display = SegmentDisplay(x = self.left, 
                                 y = self.bottom,
                                 charheight=self.charheight,
                                 charsperline = 21,
                                 numlines=2,
                                      valign='bottom')
        #display.x = display.x + display.spacing

    def get_bound(self):
        """Returns a Shapely Polygon bound for the drawing, so it may avoid intersecting the text."""
        top = self.top
        bottom = self.bottom
        left = self.left
        right = self.right
        s = self.display.spacing
        cw = self.display.charwidth
        stampright = self.display.x + self.display.getwidth()
        stamptop = bottom - self.display.charheight - s - s
        nameright = left + 15*(cw+s) + s + s 
        nametop = self.display.y - s

        bound = Polygon([(left,top),(right,top),(right,bottom),(stampright,bottom),(stampright,stamptop),(nameright,stamptop),(nameright,nametop),(left,nametop)])
        return bound
        
    def get_frame(self):
        t = 0-self.height/2.0
        b = self.height/2.0
        l = 0-self.width/2.0
        r = self.width/2.0
        return Polygon([(l,t),(r,t),(r,b),(l,b)])


    def get_border(self):
        """Return a shapely Polygon of the border"""
        top = self.top
        bottom = self.bottom
        left = self.left
        right = self.right

        border = Polygon([(left,top),(right,top),(right,bottom),(left,bottom)])
        return border

    def get_text(self):
        """Return the random seed + name as a Geometry Collection of Polygons"""
        #display = SegmentDisplay(x = self.left, 
        #                         y = self.bottom-(self.charheight*2),
        #                         charheight=self.charheight,
        #                         charsperline = 21)
        #display.y = display.y - display.spacing
        #display.y = display.y - display.spacing
        #display.x = display.x + display.spacing
        
        seedstring = f"{self.seed:#0{10}X}"
        datestring = datetime.date.today().strftime("%Y-%m-%d")
        text = "GARRISON OSTEEN\n" + datestring + " " + seedstring
        return self.display.display(text)
