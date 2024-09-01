# Bezier Utilities
import random
import numpy as np
import bezier
from shapely.geometry import LineString, Point

def bezier_to_linestring(b, granularity = 0.01):
    """Takes a Bezier curve object and converts it to a Shapely LineString."""
    points = []

    for t in np.arange(0,1,granularity):
        p = b.evaluate(t)
        x = p[0][0]
        y = p[1][0]
        points.append([x,y])

    # Feels bad, but sometimes it doesn't get all the way to one, so I'm evaluating again to make sure it hits the exact end of the curve. Surely there's a better way to do this?
    p = b.evaluate(1.0)
    x = p[0][0]
    y = p[1][0]
    points.append([x,y])

    return LineString(points)

def random_bezier(bound = 100):
    """Returns a bezier curve object with points randomized between -bound and bound."""

    x1 = random.random()*2*bound - bound
    y1 = random.random()*2*bound - bound
    x2 = random.random()*2*bound - bound
    y2 = random.random()*2*bound - bound
    x3 = random.random()*2*bound - bound
    y3 = random.random()*2*bound - bound
    x4 = random.random()*2*bound - bound
    y4 = random.random()*2*bound - bound
    nodes = [[x1,x2,x3,x4],
            [y1,y2,y3,y4]]
    return bezier.Curve.from_nodes(nodes)
