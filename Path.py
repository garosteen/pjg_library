import random

class Path:
    """
    A Path is a sequence of points.
    Use the add(other) method to try to combine multiple paths.
    If either of their start or end points are within the tolerance value,
    the other path will be added to this path.

    TODO:
    - Some sort of smoothing function?
    - Cropping -- start/end/point, percentage
    - Should you be able to add paths that aren't compatible? Connect the closest start/end points?

    How should cropping work?
    Give it a percentage, or a distance to crop?
    add should be called merge

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

    def is_loop(self):
        # TODO: should this be a boolean that gets checked when points are added or removed, or should I just call this whenever I need?
        # I guess, how computationally complex is this really?
        start = self.get_start()
        end = self.get_end()
        diff_x = abs(start[0] - end[0])
        diff_y = abs(start[1] - end[1])

        if diff_x < self.tolerance and diff_y < self.tolerance:
            return True
        return False

    def shift(self, percentage=None):
        """
        Randomly shifts the order of points, to offset the start point.
        Doesn't check that this is a loop, so you can use this at your own peril.
        """
        num_points = len(self.points)
        if percentage is None:
            percentage = random.random()
        # new_start = random.randint(0,num_points-1)
        new_start = int( percentage * num_points % num_points)
        self.points = self.points[new_start:] + self.points[:new_start]

    def crop(self, percentage = None, from_start = True):
        # Ridiculously, just going to randomly crop them for now
        # I need to choose which end to crop

        if self.is_loop():
            self.shift()
        if percentage is None:
            percentage = random.random() * 0.5
        crop_num = int(percentage * len(self.points))
        if percentage >= 1.0:
            self.points = [self.points[0]]
            return
        if from_start:
            self.points = self.points[crop_num:]
        else:
            self.points = self.points[0:len(self.points)-crop_num]

