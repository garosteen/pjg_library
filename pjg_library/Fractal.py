import math

class DragonCurve:
    """
    Possible implementation of a dragon curve:
    Give it the two "control points," i.e. the starting points of the line segment
    Give it number of iterations
    Receive a list of points
    Give or set the direction/curvature? 

    Alternative:
    Just give the number of iterations, and its up to me to scale/rotate them as needed?
    Relative to a 1-unit high and 1.5 wide bounding box, the control points are 1 unit apart, 1/3 away from the left, and 2/3 away from the top

    """
    curvature = 1

    def __init__(self, start, end, iterations, curvature = -1):
        self.points = []
        self.start = start
        self.end = end
        self.iterations = iterations
        self.curvature = curvature
        self.points.append(start)
        self.points.append(end)

        for i in range(iterations):
            # Add a point between each set of points, at half distance from center, to the left or right, alternating
            # Should I create a list of the new points, and then... interweave them?
            # I'll create a new array, and add them as I go, and then replace points with that array
            new_points = []
            previous = None
            direction = self.curvature
            new_points.append(self.points[0])
            for p in self.points:
                if previous:
                    # do stuff to calculate
                    # Find center:
                    diffx = p[0] - previous[0]
                    diffy = p[1] - previous[1]
                    dist = math.sqrt(diffx*diffx + diffy*diffy)
                    radius = dist / 2.0
                    center = ((previous[0] + p[0])/2, (previous[1] + p[1])/2)
                    angle = math.atan2(diffy, diffx)
                    # Now, from the center, to the radius, at angle + direction * PI/2
                    angle_offset = math.pi / 2.0
                    shift_angle = angle + direction * angle_offset

                    new_x = math.cos(shift_angle)*radius + center[0]
                    new_y = math.sin(shift_angle)*radius + center[1]
                    new_point = (new_x, new_y)
                    new_points.append(new_point)
                    new_points.append(p)
                    direction = direction * -1

                previous = p
            self.points = new_points
            print(len(self.points))
