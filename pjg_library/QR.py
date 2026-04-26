import qrcode
from pjg_library import utilityfunctions as uf
from pjg_private.Fill import explore_grid_from_cell
from shapely.geometry import LineString, Point, GeometryCollection
from shapely.affinity import scale, translate

def qr_path(text, size):
    # Take the text, create a QR code path from it
    #sys.setrecursionlimit(10000)
    qr = qrcode.QRCode(version=None, box_size=1, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    matrix = uf.upscale(matrix,level=2)
    rows = len(matrix)
    cols = len(matrix[0])
    paths = []
    for row in range(rows):
        for col in range(cols):

            path, backtrack = explore_grid_from_cell(matrix,row,col)
            if path is not None:
                if len(path) > 1:
                    paths.append(LineString(path))
                else:
                    paths.append(Point(path))

    scalefactor = size/rows
    paths = GeometryCollection(paths)
    paths = scale(paths,xfact=scalefactor,yfact=scalefactor,origin=(0,0))
    return paths
