import os

#
# symbols etc. are hidden away in a confusing array of packages and modules,
# and also not a big fan of the from...import... pattern, so hide that all away here
# for now, to make writing the demo a bit easier
#

from mathics.core.symbols import Symbol, SymbolList, SymbolPlus, SymbolTimes, SymbolPower, SymbolList, strip_context
from mathics.core.systemsymbols import SymbolSin, SymbolCos, SymbolArcTan, SymbolSqrt, SymbolAbs, SymbolGamma, \
    SymbolRule, SymbolI, SymbolE, SymbolPi, SymbolRow, SymbolGrid, SymbolMakeBoxes, \
    SymbolTraditionalForm, SymbolStandardForm, SymbolMathMLForm, SymbolOutputForm, SymbolTeXForm, \
    SymbolRowBox, SymbolFractionBox, SymbolSqrtBox, SymbolSuperscriptBox, SymbolHold
from mathics.core.attributes import A_HOLD_FIRST, A_PROTECTED, A_HOLD_ALL

from mathics.builtin.box.graphics import LineBox
from mathics.builtin.box.expression import BoxExpression

try:
    from mathics.core.atoms import NumericArray
except:
    pass

from mathics.core.atoms import Integer, Real, Complex, String
from mathics.core.list import ListExpression
from mathics.core.expression import Expression
from mathics.session import MathicsSession, Evaluation

from mathics.core.builtin import Builtin
from mathics.core.load_builtin import add_builtins

from mathics.core.convert.sympy import expression_to_sympy, SympyExpression

#
# where to find these?
#

SymbolHypergeometricPFQ = Symbol("System`HypergeometricPFQ")

SymbolPlotPoints = Symbol("System`PlotPoints")
SymbolPlotRange = Symbol("System`PlotRange")
SymbolAxes = Symbol("System`Axes")
SymbolColorFunction = Symbol("System`ColorFunction")
SymbolPlotLegends = Symbol("Global`PlotLegends") # TODO: move to System
SymbolBarLegend = Symbol("Global`BarLegend") # TODO: move to System
SymbolImageSize = Symbol("System`ImageSize")
SymbolAspectRatio = Symbol("System`AspectRatio")

SymbolVertexColors = Symbol("System`VertexColors")
SymbolRGBColor = Symbol("System`RGBColor")

SymbolManipulate = Symbol("System`Manipulate") # TODO: move to System
SymbolManipulateBox = Symbol("System`ManipulateBox") # TODO: move to System
SymbolGraphics3D = Symbol("System`Graphics3D")
SymbolGraphics3DBox = Symbol("System`Graphics3DBox")
SymbolGraphics = Symbol("System`Graphics")
SymbolGraphicsBox = Symbol("System`GraphicsBox")
SymbolGraphicsComplex = Symbol("System`GraphicsComplex") # TODO: move to System
SymbolLine = Symbol("System`Line")
SymbolPoint = Symbol("System`Point")
SymbolPointBox = Symbol("System`PointBox")
SymbolPolygon = Symbol("System`Polygon")
SymbolPolygonBox = Symbol("System`PolygonBox")
SymbolPolygon3DBox = Symbol("System`Polygon3DBox")
SymbolLineBox = Symbol("System`LineBox")
SymbolLine3DBox = Symbol("System`Line3DBox")

SymbolTemplateBox = Symbol("System`TemplateBox")
SymbolStyleBox = Symbol("System`StyleBox")
SymbolTagBox = Symbol("System`TagBox")
SymbolGridBox = Symbol("System`GridBox")

SymbolSequence = Symbol("System`Sequence")

SymbolGreater = Symbol("System`Greater")
SymbolLessEqual = Symbol("System`LessEqual")
SymbolIf = Symbol("System`If")
SymbolModule = Symbol("System`Module")
SymbolCompoundExpression = Symbol("System`CompoundExpression")
SymbolSet = Symbol("System`Set")
SymbolIncrement = Symbol("System`Increment")
SymbolAddTo = Symbol("System`AddTo")
SymbolTimesBy = Symbol("System`TimesBy")
SymbolDivideBy = Symbol("System`DivideBy")
SymbolFor = Symbol("System`For")

SymbolNull = Symbol("System`Null")
