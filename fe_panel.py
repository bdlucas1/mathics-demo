import panel as pn
import plotly.express as px

import core
import sym
import util
import layout as lt
import os

# start mathics session
session = core.MathicsSession()
expr = session.parse("Plot3D[Cos[x] Sin[y], {x,0,4 Pi}, {y,0, 6 Pi}]")
expr = expr.evaluate(session.evaluation)

# fake front end
class FE:
    session = session
fe = FE()

# layout for epxpression
layout = lt.expression_to_layout(fe, expr)

# wrap in panel widget
app = pn.Column(layout)

# serve it forth
app.servable()

