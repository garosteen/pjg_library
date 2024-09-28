class Path:
    """
    A Path is a sequence of points.
    Use the add(other) method to try to combine multiple paths.
    If either of their start or end points are within the tolerance value,
    the other path will be added to this path.
    TODO:
    - Some sort of smoothing function?
    - Cropping -- start/end/point, percentage

    """
    def __init__(self,start,end):
        self.points = [start,end]
        self.tolerance = 0.00001

    def get_start(self):
        return self.points[0]

    def get_end(self):
        return self.points[-1]

    def add(self,other):
        compatible = self.get_compatibility(other)

        if compatible == 0:
            # Paths are not compatible.
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
        Checks whether two paths can be combined into one path. Return code indicates
        how the paths can be combined:
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


