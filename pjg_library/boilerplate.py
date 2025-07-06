import os, sys
sys.path.append('/Users/gosteen/dev/generative/')
from pjg_library import utilityfunctions as uf
from pjg_library import SketchBorder

def boilerplate(vsk):
    paper_width_in = vsk.Param(7)
    paper_height_in = vsk.Param(10)
    target_width_in = vsk.Param(7)
    target_height_in = vsk.Param(10)
    test = vsk.Param(1)

def sketch_setup(sketch, vsk):
    sketch_width = uf.in_to_cm(sketch.paper_width_in) # 9in
    sketch_height = uf.in_to_cm(sketch.paper_height_in) # 12in
    vsk.size(width=str(sketch_width)+"cm",height=str(sketch_height)+"cm",landscape=False)
    width = uf.in_to_cm(sketch.target_width_in) 
    height = uf.in_to_cm(sketch.target_height_in)
    vsk.scale("cm")
    seed = vsk.random_seed
    sb = SketchBorder.SketchBorder(width,height,seed=seed)
    bound = sb.get_bound()
    if sketch.draw_border:
        border = sb.get_border()
        vsk.stroke(1)
        vsk.geometry(border)
        vsk.strokeWeight(1)
        vsk.geometry(sb.get_text())
    if sketch.draw_frame:
        vsk.geometry(sb.get_frame())

    return sb
