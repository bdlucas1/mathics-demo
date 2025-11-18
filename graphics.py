"""
Layout functions for GraphicsBox, Graphics3DBox, and ManipulateBox.
These functions are called by expression_to_layout in layout.py; see
comment there for general explanation of layouts.
"""

import collections 
import itertools
import numpy as np
import os

import core
import sym

from consumer import GraphicsConsumer

from mathics.core.builtin import Builtin
from mathics.core.load_builtin import add_builtins

import layout as lt
import mode
import util
import render

def layout_GraphicsXBox(fe, expr, dim):

    graphics = GraphicsConsumer(expr)

    thing = render.Thing(fe, dim, graphics.options)

    for i, (kind, vertices, item) in enumerate(graphics.items()):
        if kind is sym.SymbolPolygon:
            thing.add_polys(vertices, item)
        elif kind is sym.SymbolLine:
            thing.add_lines(vertices, item)
        elif kind is sym.SymbolPoint:
            thing.add_points(vertices, item)
        else:
            raise NotImplementedError(f"{kind}")

    figure = thing.figure()
    layout = mode.graph(figure, graphics.options.height)
    return layout

#
#
#

def layout_GraphicsBox(*args):
    return layout_GraphicsXBox(dim=2, *args)

def layout_Graphics3DBox(*args):
    return layout_GraphicsXBox(dim=3, *args)    


from manipulate import layout_ManipulateBox

layout_funs = {
    sym.SymbolManipulateBox: layout_ManipulateBox,
    sym.SymbolGraphicsBox: layout_GraphicsBox,
    sym.SymbolGraphics3DBox: layout_Graphics3DBox,
}


