"""
Layout functions for GraphicsBox, Graphics3DBox, and ManipulateBox.
These functions are called by expression_to_layout in layout.py; see
comment there for general explanation of layouts.
"""

import collections
import itertools
import os

import numpy as np
from mathics.core.builtin import Builtin
from mathics.core.load_builtin import add_builtins

import core
import layout as lt
import mode
import render
import sym
import util
from consumer import GraphicsConsumer


def layout_GraphicsBox(fe, expr, dim):

    graphics = GraphicsConsumer(expr)

    builder = render.FigureBuilder(fe, dim, graphics.options)

    for i, (kind, vertices, item) in enumerate(graphics.items()):
        if kind is sym.SymbolPolygon:
            builder.add_polys(vertices, item)
        elif kind is sym.SymbolLine:
            builder.add_lines(vertices, item)
        elif kind is sym.SymbolPoint:
            builder.add_points(vertices, item)
        else:
            raise NotImplementedError(f"{kind}")

    figure = builder.figure()
    layout = mode.graph(figure, graphics.options.height)
    return layout

#
#
#

from manipulate import layout_ManipulateBox

layout_funs = {
    sym.SymbolManipulateBox: layout_ManipulateBox,
    sym.SymbolGraphicsBox: lambda *args: layout_GraphicsBox(dim=2, *args),
    sym.SymbolGraphics3DBox: lambda *args: layout_GraphicsBox(dim=3, *args)
}


