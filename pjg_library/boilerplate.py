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

# Deprecated, use LayerManager.setup(vsk) instead
def sketch_setup(sketch, vsk, width_in =7.0, height_in =5.0):
    width_cm = uf.in_to_cm(width_in) 
    height_cm = uf.in_to_cm(height_in)
    vsk.size(width=str(width_cm)+"cm",height=str(height_cm)+"cm",landscape=False,center=False)
    vsk.scale("cm")
    seed = vsk.random_seed
    sb = SketchBorder.SketchBorder(width_cm,height_cm,seed=seed)
    bound = sb.get_bound()

    return sb
