"""
Layout functions for GraphicsBox, Graphics3DBox, and ManipulateBox.
These functions are called by expression_to_layout in layout.py; see
comment there for general explanation of layouts.
"""

import collections 
import itertools
import numpy as np
import os

from mathics.core.builtin import Builtin
from mathics.core.load_builtin import add_builtins

import layout as lt
import mcs
import mode
import util
import render

#
# Manipulate builtin
#

class Manipulate(Builtin):

    attributes = mcs.A_HOLD_FIRST

    # TODO: expr is held so it arrives here safely, but for some reason by the time it
    # gets to eval_makeboxes it has some funky HoldForm's interspersed. To see that,
    # comment this eval out and look at the expr in eval_makeboxes. Don't know why or how to avoid.
    # So hack: immediately turn it into a String, then re-parse in eval_makeboxes.
    # There must be a better way.
    def eval(self, evaluation, expr, sliders):
        "Manipulate[expr_, sliders___]"
        if not isinstance(expr, mcs.String):
            return mcs.Expression(mcs.SymbolManipulate, mcs.String(str(expr)), sliders)
        return None

    def eval_makeboxes(self, evaluation, expr, sliders, form, *args, **kwargs):
        "MakeBoxes[Manipulate[expr_, sliders___], form:StandardForm|TraditionalForm|OutputForm|InputForm]"
        expr = evaluation.parse(expr.value) # hack - see note above
        return ManipulateBox(expr, sliders)


    """
    options = {
        "Axes": "{False, True}",
        "AspectRatio": "1 / GoldenRatio",
    }
    """

# TODO: Mathematica does something more complicated, and more general,
# involving DynamicModule, Dymanic, Dynamic*Box, etc.
# Do we want to emulate that?
class ManipulateBox(mcs.BoxExpression):
    def __init__(self, expr, sliders):
        super().__init__(self, expr, sliders)

# regarding expression=False: see mathics/core/builtin.py:221 "can be confusing"
add_builtins([("System`Manipulate", Manipulate(expression=False))])


#
# given a ManipulateBox Expression, compute a layout
#

def layout_ManipulateBox(fe, manipulate_expr):

    target_expr = manipulate_expr.elements[0]
    slider_expr = manipulate_expr.elements[1]

    # TODO: slider_expr came from matching an ___ pattern in Manipulate (see above)
    # According to Mathematica documentation(?), the ___ notation is meant to take
    # the rest of elements and wrap them in a List, even if there is only one.
    # Instead we get just the element if only one, and the elements in a Sequence (not List) if >1
    # Am I doing something wrong or misunderstanding?
    if slider_expr.head == mcs.SymbolSequence:
        slider_specs = [s.to_python() for s in slider_expr.elements]
    else:
        slider_specs = [slider_expr.to_python()]

    # parse slider specs
    S = collections.namedtuple("S", ["name", "lo", "init", "hi", "step"])
    def slider(spec):
        v, lo, hi = spec[0:3]
        step = spec[3] if len(spec) > 3 else (hi-lo)/10 # TODO: better default step
        v, init = v if isinstance(v, (list,tuple)) else (v, lo)
        v = str(v).split("`")[-1] # strip off namespace pfx
        spec = S(v, lo, init, hi, step)
        return spec
    sliders = [slider(spec) for spec in slider_specs]

    # compute a layout for an expr given a set of values
    # this is the callback for this Manipulate to update the target with new values
    def eval_and_layout(values):
        # TODO: always Global?
        # TODO: always Real?
        # TODO: best order for replace_vars and eval?
        values = {s.name: a for s, a in zip(sliders, values)}
        with util.Timer("replace and eval"):
            expr = target_expr.replace_vars({"Global`"+n: mcs.Real(v) for n, v in values.items()})
            expr = expr.evaluate(fe.session.evaluation)
        with util.Timer("layout"):
            layout = lt.expression_to_layout(fe, expr)
        return layout

    # compute the layout for the plot
    init_values = [s.init for s in sliders]
    init_target_layout = eval_and_layout(init_values)
    layout = mode.manipulate(init_target_layout, sliders, eval_and_layout)
        
    return layout



#
# traverse a Graphics or Graphics3D expression and collect points, lines, and triangles
# as numpy arrays that are efficient to traverse
#
# TODO: can this be plugged into existing machinery for processing Graphics and Graphics3D?
# there seems to be a bunch of stuff related to this in mathics.format that could be reused,
# but it currently seems to assume that a string is being generated to be saved in a file
#

from mathics.core.symbols import (
    SymbolList,
    Symbol,
)    
from mathics.core.systemsymbols import (
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolGraphicsComplex,
    SymbolPolygon,
    SymbolRule,
    SymbolAutomatic,
    SymbolLine,
    SymbolPoint,
)
from mathics.core.expression import Expression
SymbolGraphics3DBox = Symbol("Graphics3DBox")
SymbolGraphicsBox = Symbol("GraphicsBox")
SymbolGraphicsComplexBox = Symbol("GraphicsComplexBox")
SymbolPolygonBox = Symbol("PolygonBox")
SymbolPolygon3DBox = Symbol("Polygon3DBox")
SymbolLineBox = Symbol("LineBox")
SymbolLine3DBox = Symbol("Line3DBox")
SymbolPointBox = Symbol("PointBox")
SymbolImageSize = Symbol("ImageSize")
SymbolAxes = Symbol("Axes")
SymbolHue = Symbol("Hue")


from mathics.core.atoms import NumericArray

import os

from typing import Optional

# where possible things are converted to np.ndarray
#   (not possible e.g. in lists of items, which may be non-homogeneous)
# indexes are converted from 1-based to 0-based TODO not yet
# where possible, lists of items are coalesced by kind

Waiting = collections.namedtuple("Waiting", ["kind", "vertices", "items"])

class GraphicsConsumer:

    # if None, we are not in a GraphicsComplex, and a coordinate is a list of xy[z]
    # if not None, we are in a GraphicsComplex, and a coordinate is an integer index into vertices
    vertices: Optional[list] = None

    # this coalesces consecutive items of the same kind
    waiting = None

    def __init__(self, expr):
        assert expr.head in (SymbolGraphics, SymbolGraphics3D, SymbolGraphicsBox, SymbolGraphics3DBox)

        self.dim = 3 if expr.head in (SymbolGraphics3D, SymbolGraphics3DBox) else 2
        self.expr = expr
        self.vertices = None
        self.graphics = expr.elements[0]

        # collect options
        class Options:
            pass
        self.options = Options()

        # TODO: these are not being passed through
        self.options.showscale = False
        self.options.colorscale = "viridis"

        def want_list(value, n=self.dim):
            if isinstance(value, list):
                assert len(value) == self.dim
                value = [None if v == "System`Automatic" else v for v in value]
            else:
                value = [value] * n
            return value

        # TODO: move to core
        SymbolAspectRatio = Symbol("AspectRatio")
        SymbolAxesStyle = Symbol("AxesStyle")
        SymbolBackground = Symbol("Background")
        SymbolBoxRatios = Symbol("BoxRatios")
        SymbolImageSize = Symbol("ImageSize")
        SymbolLabelStyle = Symbol("LabelStyle")
        SymbolLighting = Symbol("Lighting")
        SymbolPlotRange = Symbol("PlotRange")
        SymbolPlotRangePadding = Symbol("PlotRangePadding")
        SymbolTicksStyle = Symbol("TicksStyle")
        SymbolViewPoint = Symbol("ViewPoint")

        for rule in expr.elements[1:]:
            assert rule.head == SymbolRule
            name = rule.elements[0]
            value = rule.elements[1].to_python()
            if value == "System`Automatic":
                value = None
            if name == SymbolAxes:
                value = want_list(value)
                # TODO: assume bool or Automatic are only options
                value = [v if isinstance(v,bool) else True for v in value]
                self.options.axes = value
            elif name == SymbolAspectRatio:
                assert isinstance(value, (int,float))
                # TODO use 
            elif name == SymbolImageSize:
                if value is None:
                    value = (300, 300)
                else:
                    value = want_list(value, 2)
                    assert isinstance(value[0], (int,float))
                self.options.width, self.options.height = value
            elif name == SymbolPlotRange:
                # TODO: what is the meaning in Graphics? and why is original value not passed through?
                value = want_list(value)
                # TODO ugh, don't unpack
                if self.dim == 3:
                    self.options.x_range, self.options.y_range, self.options.z_range = value
                else:
                    self.options.x_range, self.options.y_range = value
            elif name in (
                    SymbolAxesStyle, SymbolBackground, SymbolBoxRatios, SymbolLabelStyle,
                    SymbolLighting, SymbolPlotRangePadding, SymbolTicksStyle, SymbolViewPoint,
                    
            ):
                pass
                # TODO: use
            else:
                #raise ValueError(f"unknown rule {name}")
                print(f"unknown rule {name}")


    def process_array(self, array):
        if isinstance(array, NumericArray):
            return array.value
        else:
            raise ValueError(f"array type is {type(array)}")

    def item(self, kind, expr, wanted_depth):

        if isinstance(expr, NumericArray):
            items = expr.value
        elif isinstance(expr, Expression):
            items = expr.to_python()

        # make items uniformly a list of items, never just a single item
        depth = lambda x: 1 + depth(x[0]) if isinstance(x, (list,tuple,np.ndarray)) else 0
        if self.vertices is None:
            wanted_depth += 1
        while depth(items) < wanted_depth:
            items = [items]

        # each item is homogeneous so we can make it an array
        items = [np.array(item) for item in items]

        # convert 1-based indexes to 0-based
        if self.vertices is not None:
            for item in items:
                item -= 1

        # flush if needed, add our items to waiting items
        if self.waiting is None:
            self.waiting = Waiting(kind, self.vertices, items)
        elif self.waiting.kind == kind and self.waiting.vertices is self.vertices:
            self.waiting.items.extend(items)
        else:
            yield self.waiting
            self.waiting = Waiting(kind, self.vertices, items)

    def flush(self):
        """ Flush any waiting items """
        if self.waiting is not None:
            yield self.waiting

    def process(self, expr):

        if expr.head == SymbolList:
            for e in expr:
                yield from self.process(e)

        elif expr.head in (SymbolGraphicsComplex, SymbolGraphicsComplexBox):
            # TODO: allow elements for array
            self.vertices = self.process_array(expr.elements[0])
            for e in expr.elements[1:]:
                yield from self.process(e)
            self.vertices = None
            yield from self.flush()

        # TODO: rationalize treatment of poly, line, point top to bottom
        # coalescing, depth, etc. is not uniform
        # poly:  [p q r ...]
        # line:  [p q r ...]
        # point: p ...
        elif expr.head in (SymbolPolygon, SymbolPolygonBox, SymbolPolygon3DBox):
            yield from self.item(SymbolPolygon, expr.elements[0], wanted_depth=3)
        elif expr.head in (SymbolLine, SymbolLineBox, SymbolLine3DBox):
            yield from self.item(SymbolLine, expr.elements[0], wanted_depth=2)
        elif expr.head in (SymbolPoint, SymbolPointBox):
            yield from self.item(SymbolPoint, expr.elements[0], wanted_depth=1)

        elif expr.head == SymbolHue:
            print("xxx skipping", expr.head, " for now")
        else:
            raise ValueError(f"unknown {expr}")


            

    def items(self):

        # process the items
        yield from self.process(self.graphics)

        # flush anything still waiting
        yield from self.flush()

def layout_GraphicsXBox(fe, expr, dim):

    graphics = GraphicsConsumer(expr)

    thing = render.Thing(dim, graphics.options)

    for i, (kind, vertices, items) in enumerate(graphics.items()):

        if kind is SymbolPolygon:

            # try stacking the items into a single array for more efficient processing
            # this works if all are the same degree poly, which will be typical
            try:
                #print("xxx stacking", len(items), "items; shape of first is", items[0].shape)
                items = [np.vstack(items)]
            except ValueError:
                print("ugh, can't stack")

            for mesh in items:

                #print("xxx mesh", mesh.shape)
                if vertices is None:
                    with util.Timer("make vertices"):
                        vertices = mesh.reshape(-1, 3)
                        mesh = np.arange(len(vertices)).reshape(mesh.shape[:-1])

                with util.Timer("triangulate"):
                    ijks = []
                    ngon = mesh.shape[1]
                    for i in range(1, ngon-1):
                        inx = [0, i, i+1]
                        tris = mesh[:, inx]
                        ijks.extend(tris)
                    ijks = np.array(ijks)

                thing.add_mesh(vertices, ijks)

        elif kind is SymbolLine:

            thing.add_lines(vertices, items)

        elif kind is SymbolPoint:
            thing.add_points(vertices, np.array(items))

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


layout_funs = {
    mcs.SymbolManipulateBox: layout_ManipulateBox,
    mcs.SymbolGraphicsBox: layout_GraphicsBox,
    mcs.SymbolGraphics3DBox: layout_Graphics3DBox,
}


