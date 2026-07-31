import math
# Distortion functions take arrays of points and smoothly distort them according to different rules/patterns
# TODO: should this be a class, or just a list of functions like this?
# Advantages to a class: 
# - set resolution globally, instead of passing into every function

"""
Takes an array of tuples, a move function, and a resolution
Returns a new array of tuples with each point smoothly adjusted according to the move function,
new points are added to keep final distance between points within resolution

move_function should be a function that takes a single tuple and returns a single tuple
It should be continuous, large jumps or discontinuities will probably break this.
"""
def distort_points(points, move_function, resolution):
    new_points = []
    previous = None
    for p in points:
        new_points = new_points + smooth_move_point(previous, p, move_function, resolution = resolution)
        previous = p
    return new_points

def extend(start, end, extension):
    length = math.dist(end, start)
    # Find the unit vector in the direction of start to end
    # Multiply by the extension length
    # Add it to the end point
    cx = end[0] + (end[0] - start[0]) / length * extension
    cy = end[1] + (end[1] - start[1]) / length * extension
    return (cx,cy)


def ripple(points, center, amplitude=1.0, wavelength=1.0, phase=0.0, resolution=1.0):
    # TODO: probably need a wavelength, amplitude, etc.
    move_function = ripple_move(center, amplitude, wavelength, phase)
    return distort_points(points, move_function, resolution)

def ripple_move(center, amplitude=1.0, wavelength=1.0, phase=0.0):
    def move(point):
        d = math.dist(point, center)
        offset = amplitude*math.sin(d/wavelength + phase) 
        return extend(center, point, offset)
    return move

def whitehole(points, center, strength, resolution):
    move_function = whitehole_move(center, strength)
    return distort_points(points, move_function, resolution)


def whitehole_move(center, strength):
    def move(point):
        d = math.dist(point, center)
        if d > 2*strength:
            return point
        if d == 0:
            nudge = 0.0001
            point = (point[0] + nudge, point[1] + nudge)
            d = math.dist(point,center)
        push = ((d-(2*strength))**2)/(4*strength)
        cx = point[0] + (point[0] - center[0]) / d * push
        cy = point[1] + (point[1] - center[1]) / d * push
        new_point = (cx,cy)
        return new_point
    return move

def smooth_move_point(prev, current, move_function, resolution):
    new_points = []
    if (prev is None):
        new_points.append(move_function(current))
        return new_points
    new_prev = move_function(prev)
    new_current = move_function(current)
    gap = math.dist(new_prev, new_current)
    if (gap > resolution):
        halfway_point = ( (prev[0] + current[0]) / 2.0, 
                         (prev[1] + current[1]) / 2.0)
        new_points = new_points + smooth_move_point(prev, halfway_point, move_function, resolution)
        new_points = new_points + smooth_move_point(halfway_point, current, move_function, resolution)
    new_points.append(new_current)
    return new_points
