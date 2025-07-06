from shapely.geometry import LineString, Point
import math

def diffract(source, dest, lens: LineString, rays = 360, num_layers=6):
    # TODO: Does the lens HAVE to be a LineString? I would like to use an array of linestrings.
    sp = Point(0,0)
    dp = Point(0,0)

    if num_layers<=0:
        num_layers=1

    layers = []
    for _ in range(num_layers):
        layers.append([])

    for r in range(rays):
        step = r/rays
        if step < 0:
            step = 0.0
        if step > 1:
            step = 1.0
        if source.geom_type == 'LineString':
            sp = source.interpolate(step, normalized=True)
        elif source.geom_type == 'Point':
            sp = source
        if dest.geom_type == 'LineString' or dest.geom_type == 'Polygon':
            dp = dest.interpolate(step, normalized=True)
        elif dest.geom_type == 'Point':
            dp = dest

        ray = LineString([sp,dp])
        intersection = ray.intersection(lens)
        geom_type = intersection.geom_type
        points = []
        if geom_type == 'Point':
            # Just a single intersection
            #print('Point intersection.')
            points.append((intersection.x,intersection.y))
            #print(points)
        elif geom_type == 'LineString':
            # A whole line intersection
            #print('Line intersection.')
            #print(intersection.coords)
            coords = list(intersection.coords)
            #print(coords)
            if len(coords) == 2:
                # TODO: Why did I decide to only do this if there are two coords?
                # Maybe instead of coords[1] I should do coords[-1]?
                points.append(coords[0])
                points.append(coords[1])
        else:
            # More than one point/line intersection
            for p in intersection.geoms:
                if p.geom_type == 'Point':
                    points.append((p.x,p.y))
                elif p.geom_type == 'LineString':
                    points.append(p.coords[0])
                    points.append(p.coords[1])

        # Sort points according to distance to source
        points.sort(key = lambda p: math.dist(p,(sp.x,sp.y)))

        for i,p in enumerate(points):
            if i == 0:
                # Skip the first portion 
                # TODO: this should be configurable/toggleable
                continue
            start = (points[i-1][0],points[i-1][1])
            end = (p[0],p[1])
            #layers[i%len(layers)].add(dwg.line(start=start,end=end,opacity=0.4,stroke_width=0.5))
            layers[i%len(layers)].append(LineString([start,end]))
    return layers
