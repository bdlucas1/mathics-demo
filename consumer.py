import collections
import os
from typing import Optional

import numpy as np

import core
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

class GraphicsOptions:

    def __init__(self, fe, expr, dim):

        options = expr.get_option_values(expr.elements[1:])

        def get_option(name, want_list=None):
            x = options[name]
            x = x.to_python()
            auto = lambda x: None if x=="System`Automatic" else x
            if want_list:
                if not isinstance(x, (list,tuple)):
                    x = [x] * want_list
                x.extend([None] * (want_list - len(x)))
                x = [auto(xx) for xx in x]
            else:
                x = auto(x)
            #print(name, x)
            return x

        # TODO
        axes_style = get_option("System`AxesStyle", 3)
        background = get_option("System`Background")
        label_style = get_option("System`LabelStyle")
        plot_range_padding = get_option("System`PlotRangePadding")
        tick_style = get_option("System`TicksStyle", 3)
        if dim==3:
            box_ratios = get_option("System`BoxRatios", 3)
            lighting = get_option("System`Lighting")
            viewpoint = get_option("System`ViewPoint", 3)
        # TODO: add showscale, colorscale, boxed

        # Axes
        self.axes = get_option("System`Axes", 3)

        # ImageSize, AspectRatio
        # TODO: pass inside_row, inside_list flags in the {} below - need a layout_options arg that we pass down
        self.image_size = expr._get_image_size({}, options, None)[0:2]
        
        # PlotRange
        self.plot_range = get_option("System`PlotRange", 3)

        #for n, v in options.items(): print(n, v)
        #for n, v in self.__dict__.items(): print(n, v)



class GraphicsConsumer:

    # if None, we are not in a GraphicsComplex, and a coordinate is a list of xy[z]
    # if not None, we are in a GraphicsComplex, and a coordinate is an integer index into vertices
    vertices: Optional[list] = None

    # this coalesces consecutive items of the same kind
    waiting = None

    def __init__(self, fe, expr):
        assert expr.head in (sym.SymbolGraphics, sym.SymbolGraphics3D, sym.SymbolGraphicsBox, sym.SymbolGraphics3DBox)

        self.dim = 3 if expr.head in (sym.SymbolGraphics3D, sym.SymbolGraphics3DBox) else 2
        self.expr = expr
        self.vertices = None
        self.graphics = expr.elements[0]

        # TODO: these are not being passed through
        self.options = GraphicsOptions(fe, expr, self.dim)
        self.options.showscale = False
        self.options.colorscale = "viridis"


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

            # stack items if possible for more efficent processing
            items = self.waiting.items
            try:
                msg = f"stacked {len(items)} {self.waiting.kind} to"
                items = [np.vstack(items)]
                print(f"{msg} [{items[0].shape}]")
            except ValueError:
                shapes = np.array([item.shape for item in items])
                print(f"can't stack {len(items)} {self.waiting.kind} {shapes}")

            for item in items:
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

        # TODO: why wanted_depth??
        elif expr.head in (sym.SymbolPolygon, sym.SymbolPolygonBox, sym.SymbolPolygon3DBox):
            yield from self.item(sym.SymbolPolygon, expr.elements[0], wanted_depth=3)
        elif expr.head in (sym.SymbolLine, sym.SymbolLineBox, sym.SymbolLine3DBox):
            yield from self.item(sym.SymbolLine, expr.elements[0], wanted_depth=3)
        elif expr.head in (sym.SymbolPoint, sym.SymbolPointBox):
            yield from self.item(sym.SymbolPoint, expr.elements[0], wanted_depth=2)

        elif expr.head == sym.SymbolHue:
            print("xxx skipping", expr.head, " for now")
        else:
            raise ValueError(f"unknown {expr}")
            

    def items(self):

        # process the items
        yield from self.process(self.graphics)

        # flush anything still waiting
        yield from self.flush()

