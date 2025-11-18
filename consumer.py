from typing import Optional
import collections
import core
import numpy as np
import os
import sym


#
# traverse a Graphics or Graphics3D expression and collect points, lines, and triangles
# as numpy arrays that are efficient to traverse
#
# TODO: can this be plugged into existing machinery for processing Graphics and Graphics3D?
# there seems to be a bunch of stuff related to this in mathics.format that could be reused,
# but it currently seems to assume that a string is being generated to be saved in a file
#



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
        assert expr.head in (sym.SymbolGraphics, sym.SymbolGraphics3D, sym.SymbolGraphicsBox, sym.SymbolGraphics3DBox)

        self.dim = 3 if expr.head in (sym.SymbolGraphics3D, sym.SymbolGraphics3DBox) else 2
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

        for rule in expr.elements[1:]:
            assert rule.head == sym.SymbolRule
            name = rule.elements[0]
            value = rule.elements[1].to_python()
            if value == "System`Automatic":
                value = None
            if name == sym.SymbolAxes:
                value = want_list(value)
                # TODO: assume bool or Automatic are only options
                value = [v if isinstance(v,bool) else True for v in value]
                self.options.axes = value
            elif name == sym.SymbolAspectRatio:
                assert isinstance(value, (int,float))
                # TODO use 
            elif name == sym.SymbolImageSize:
                if value is None:
                    value = (300, 300)
                else:
                    value = want_list(value, 2)
                    assert isinstance(value[0], (int,float))
                self.options.width, self.options.height = value
            elif name == sym.SymbolPlotRange:
                # TODO: what is the meaning in Graphics? and why is original value not passed through?
                value = want_list(value)
                # TODO ugh, don't unpack
                if self.dim == 3:
                    self.options.x_range, self.options.y_range, self.options.z_range = value
                else:
                    self.options.x_range, self.options.y_range = value
            elif name in (
                    sym.SymbolAxesStyle, sym.SymbolBackground, sym.SymbolBoxRatios, sym.SymbolLabelStyle,
                    sym.SymbolLighting, sym.SymbolPlotRangePadding, sym.SymbolTicksStyle, sym.SymbolViewPoint,
                    
            ):
                pass
                # TODO: use
            else:
                #raise ValueError(f"unknown rule {name}")
                print(f"unknown rule {name}")


    def process_array(self, array):
        if isinstance(array, core.NumericArray):
            return array.value
        else:
            raise ValueError(f"array type is {type(array)}")

    def item(self, kind, expr, wanted_depth):

        if isinstance(expr, core.NumericArray):
            items = expr.value
        elif isinstance(expr, core.Expression):
            items = expr.to_python()

        # make items uniformly a list of items, never just a single item
        depth = lambda x: 1 + depth(x[0]) if isinstance(x, (list,tuple,np.ndarray)) else 0
        if self.vertices is None:
            wanted_depth += 1
        while depth(items) < wanted_depth:
            items = [items]

        # each item must be homogeneous so we can make it an array
        items = [np.array(item) for item in items]

        # stack items if possible for more efficent processing
        try:
            items = [np.vstack(items)]
        except ValueError:
            print("ugh, can't stack")

        # convert 1-based indexes to 0-based if in GraphicsComplex
        if self.vertices is not None:
            for item in items:
                item -= 1

        # flush if needed, add our items to waiting items
        if self.waiting is None:
            self.waiting = Waiting(kind, self.vertices, items)
        elif self.waiting.kind == kind and self.waiting.vertices is self.vertices:
            self.waiting.items.extend(items)
        else:
            yield from self.flush()
            self.waiting = Waiting(kind, self.vertices, items)

    def flush(self):
        """ Flush any waiting items """
        if self.waiting is not None:
            for item in self.waiting.items:
                yield self.waiting.kind, self.waiting.vertices, item
            self.waiting = None

    def process(self, expr):

        if expr.head == sym.SymbolList:
            for e in expr:
                yield from self.process(e)

        elif expr.head in (sym.SymbolGraphicsComplex, sym.SymbolGraphicsComplexBox):
            # TODO: allow elements for array
            self.vertices = self.process_array(expr.elements[0])
            for e in expr.elements[1:]:
                yield from self.process(e)
            self.vertices = None
            yield from self.flush()

        elif expr.head in (sym.SymbolPolygon, sym.SymbolPolygonBox, sym.SymbolPolygon3DBox):
            yield from self.item(sym.SymbolPolygon, expr.elements[0], wanted_depth=2)
        elif expr.head in (sym.SymbolLine, sym.SymbolLineBox, sym.SymbolLine3DBox):
            yield from self.item(sym.SymbolLine, expr.elements[0], wanted_depth=2)
        elif expr.head in (sym.SymbolPoint, sym.SymbolPointBox):
            yield from self.item(sym.SymbolPoint, expr.elements[0], wanted_depth=1)

        elif expr.head == sym.SymbolHue:
            print("xxx skipping", expr.head, " for now")
        else:
            raise ValueError(f"unknown {expr}")
            

    def items(self):

        # process the items
        yield from self.process(self.graphics)

        # flush anything still waiting
        yield from self.flush()

