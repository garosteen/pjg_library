import os, sys
sys.path.append('/Users/gosteen/dev/generative/')
from pjg_library import utilityfunctions as uf
from pjg_library import SketchBorder

def boilerplate(vsk):
    paper_width_in = vsk.Param(11.0)
    paper_height_in = vsk.Param(14.0)
    target_width_in = vsk.Param(11.0)
    target_height_in = vsk.Param(14.0)
    test = vsk.Param(1)

def sketch_setup(sketch, vsk):
    sketch_width = uf.in_to_cm(sketch.paper_width_in) # 9in
    sketch_height = uf.in_to_cm(sketch.paper_height_in) # 12in
    vsk.size(width=str(sketch_width)+"cm",height=str(sketch_height)+"cm",landscape=False,center=False)
    width = uf.in_to_cm(sketch.paper_width_in) 
    height = uf.in_to_cm(sketch.paper_height_in)
    vsk.scale("cm")
    seed = vsk.random_seed
    sb = SketchBorder.SketchBorder(width,height,seed=seed)
    bound = sb.get_bound()

    return sb
