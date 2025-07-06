from .SegmentCodes import *
from .SegmentLines import *
from shapely.geometry import Polygon,GeometryCollection,LineString
from shapely.ops import polygonize_full,linemerge,unary_union
class SegmentDisplay:
    """
    TODO:
        - How to use Enums? I want to be able to basically say, display.align(SegmentDisplay.TOP) or something like that.
        - vertical and horizontal spacing should be separate params
        - set/get methods for various parameters?
        - get all segments for 'unilluminated' background characters, either customizable number of characters or using previous text as memory
        - Some character should make it return a fully-illuminated response.
        - Could use 'defaultdict' type to ensure return type of unrecognized characters
        - Is display rotation feasible, or should that be handled by the caller?
        - Should this class really handle conversion to GeometryCollection? How else could that be handled elegantly?
        - Make a way to toggle between some different display styles -- lines, classic, starburst, etc.

        - set mode for alignment - halign = center, left, right, valign = top, center, bottom
        - Set mode: flexible, fixed

        What would make this MOST user-friendly?
        I create a "display". Give it size parameters. 
        Should the default alignment be left, top, or centered? Probably left, for most use cases.
        I'm actually finding that I typically want it centered?
    """
    def __init__(self,x=0,y=0,charheight=1.0,relative_width=0.5,relative_spacing=0.2,charsperline=0,numlines=1,halign='left',valign='top',fixedwidth=False,fixedheight=False,wrap=False):
        self.text = [[' ' for c in range(charsperline)] for l in range(numlines)]
        self.x = x
        self.y = y
        self.charheight = charheight
        self.charwidth = self.charheight*relative_width
        self.spacing = self.charwidth*relative_spacing
        self.codes = fourteen_segment_codes
        self.charsperline = charsperline
        self.numlines = numlines
        #self.display = fourteen_segment_lines
        self.display_style = fourteen_segment_rectangles
        self.linechars = 0
        self.fixedwidth = fixedwidth
        self.fixedheight = fixedheight
        self.wrap = wrap
        self.halign = halign
        self.valign = valign

    def get_position(self):
        """Get the x,y coordinates of the top left of the display."""
        width = len(self.text[0]) * (self.spacing + self.charwidth) + self.spacing
        height = len(self.text) * (self.spacing + self.charheight) + self.spacing
        # left, top is the default
        x = self.x
        y = self.y

        if self.halign == 'center':
            x = self.x - width/2.0
        elif self.halign == 'right':
            x = self.x - width

        if self.valign == 'center':
            y = self.y - height/2.0
        elif self.valign == 'bottom':
            y = self.y - height

        return (x,y)

    def addColumns(self,numColumns=1):
        for line in self.text:
            for column in range(numColumns):
                line.append(' ')

    def addRows(self,numRows=1):
        for row in range(numRows):
            self.text.append([' ' for c in range(len(self.text[0]))])
    
    def setText(self,text,line=0,char=0):
        # By default, too-long strings should just expand the charsperline
        # But there should be an option to FIX the width of the display
        # Then, overflows can either go to next line, or be truncated, depending on an option?

        # handle case where self.text is uninitialized
        # Too many lines can either expand the numlines, or truncate if fixed
        # Can this take an array, or should it only take a single string?
        # \n can be interpreted correctly, as newline behavior, but what about arrays?
        # I'm gonna say NO arrays, only text strings.
        # Does a newline preserve the char index you started with? Probably that would be good.
        # TODO: check that char and line are within bounds first
        if char < 0 or line < 0:
            # Just don't fuck with this.
            return

        pos = [line, char]
        for c in text:
            if c == '\n':
                pos[0] = pos[0] + 1
                pos[1] = char
            else:
                while not self.checkPosition(pos):
                    if not self.fixedwidth:
                        self.expandToPosition(pos)
                    elif self.wrap:
                        pos[0] = pos[0] + 1
                        pos[1] = char
                    else:
                        # fixed width, can't wrap, position is invalid.
                        return
                # Position is valid
                self.text[pos[0]][pos[1]] = c
                pos[1] += 1

    def checkPosition(self,pos):
        row, char = pos
        # Will this condition work if row is out of bounds?
        return 0 <= row < len(self.text) and 0 <= char < len(self.text[row])

    def expandToPosition(self,pos):
        row, char = pos
        if (row >= len(self.text)):
            self.addRows(row - len(self.text) + 1)
        if (char >= len(self.text[row])):
            self.addColumns(char - len(self.text[row]) + 1)

    def getwidth(self):
        return self.charsperline * (self.charwidth + self.spacing)

    def scale(self, scale):
        self.charheight = self.charheight*scale
        self.charwidth = self.charwidth*scale
        self.spacing = self.spacing*scale

    def get_segments(self):
        charsegments = []
        for lineindex, line in enumerate(self.text):
            for charindex, char in enumerate(line):
                charsegments.append(self.get_character_segments(char,lineindex,charindex))

        return charsegments 

    def get_character_segments(self,character,lineindex,charindex):
        xoffset = (self.charwidth + self.spacing) * charindex + self.spacing
        yoffset = (self.charheight + self.spacing) * lineindex + self.spacing

        indices = self.get_character_indices(character)
        segments = []
        position = self.get_position()
        for index in indices:
            basesegment = self.display_style[index]
            adjusted_segment = []
            for point in basesegment:
                x = point[0]*self.charwidth + position[0] + xoffset
                y = point[1]*self.charheight + position[1] + yoffset
                adjusted_segment.append([x,y])
            segments.append(adjusted_segment)

        return segments

    def get_character_indices(self,character):
        hexval = self.get_hex(character)
        indices = []
        for i in range(15):
            if hexval >> i & 1:
                indices.append(i)
        return indices

    def get_hex(self, character):
        return self.codes[character]

    def get_unions(self):
        """Merges segments in each letter into fewer polygons to reduce overlapping elements."""
        segments = self.get_segments()
        unions = []
        for letter in segments:
            polygons = []
            for segment in letter:
                polygons.append(Polygon(segment))
            unions.append(unary_union(polygons))
        return unions

    def get_geom_collection(self):
        segments = self.get_segments()
        multipolys = []
        for letter in segments:
            for segment in letter:
                if len(segment) < 3:
                    multipolys.append(LineString(segment))
                else:
                    poly = Polygon(segment)
                    multipolys.append(poly)

        return  GeometryCollection(multipolys)

    def get_array_geom_collection(self):
        segments = self.get_segments()
        geoms = []
        for letter in segments:
            multipolys = []
            for segment in letter:
                poly = Polygon(segment)
                multipolys.append(poly)
            geoms.append(GeometryCollection(multipolys))

        return geoms

    def move(self,x,y):
        self.x = x
        self.y = y

    def display(self, text=None):
        if text is not None:
            self.setText(text)
        return GeometryCollection(self.get_unions())

if __name__ == '__main__':
    d = SegmentDisplay()
