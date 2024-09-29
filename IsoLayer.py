from pjg_library.Path import Path

class IsoLayer:
    """
    An Isolayer represents a collection of contour curves for a specific value.
    TODO:
    - Make interpolation optional, so you can keep things geometric if you want.
    """

    def __init__(self,value):
        self.value = value
        self.curves = []

    def get_curves(self):
        return self.curves

    def add(self,start,end):
        """
        Given the start and end points of a segment, add that segment to this IsoLayer.
        If it matches the start or end of any existing paths, it will be appended to that path.
        Otherwise, it's added as a new path.

        TODO:
        Are there more efficient ways to merge the paths?
        I'm currently checking the path compatibility twice for each join.
        What if the ends of the paths were in a sort of quad tree, so we only check things that are likely to be close?
        """
        # Check if line is compatible with any others
        curve = Path(start,end)
        match_1 = -1
        match_2 = -1
        for index,other in enumerate(self.curves):
            compat = curve.get_compatibility(other)
            if compat != 0:
                if match_1 == -1:
                    match_1 = index
                else:
                    match_2 = index
                    break
        
        if match_1 == -1:
            # No match, just add the curve
            self.curves.append(curve)
        else:
            self.curves[match_1].add(curve)
            if match_2 != -1:
                self.curves[match_2].add(self.curves[match_1])
                self.curves.pop(match_1)

    def marching_squares(self, row, col, topleft, topright, botleft, botright):
        """
        For the given corner values and row/col, use marching squares to add the correct
        path to this Isolayer.
        """
        top_interp = 0.5
        bot_interp = 0.5
        right_interp = 0.5
        left_interp = 0.5
        val = self.value

        flags = 0
        if topleft > val:
            flags += 1
        if topright > val:
            flags += 2
        if botright > val:
            flags += 4
        if botleft > val:
            flags += 8

        if flags == 0 or flags == 15:
            # There is no contour here
            return
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
            self.add(left,top)
        elif flags == 2 or flags == 13:
            self.add(top,right)
        elif flags == 3 or flags == 12:
            self.add(left,right)
        elif flags == 4 or flags == 11:
            self.add(right,bottom)
        elif flags == 5:
            self.add(top,right)
            self.add(left,bottom)
        elif flags == 6 or flags == 9:
            self.add(top,bottom)
        elif flags == 7 or flags == 8:
            self.add(left,bottom)
        elif flags == 10:
            self.add(left,top)
            self.add(bottom,right)

