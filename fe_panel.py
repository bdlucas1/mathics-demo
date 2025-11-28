import panel as pn
import panel.widgets as pnw
import plotly.express as px
import plotly.graph_objects as go
import ipywidgets as ipw

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

#################


# Text input widget
text_input = pn.widgets.TextInput(
    name="Data",
    placeholder="Enter numbers, then press Enter",
    value = "Plot3D[Cos[x] Sin[y], {x,0,4 Pi}, {y,0, 6 Pi}]"
)

# Output pane
#plot_pane = pn.pane.Plotly(height=400)
plot_pane = pn.pane.IPyWidget(ipw.HBox(), height=400)
#help(pn.pane.IPyWidget)

# Callback that runs whenever Enter commits the new value
def update_plot(event):
    expr = text_input.value
    expr = session.parse(expr)
    expr = expr.evaluate(session.evaluation)
    layout = lt.expression_to_layout(fe, expr)

    plot_pane.object = layout

# Trigger update when value changes (Enter key)
text_input.param.watch(update_plot, "value")

# Layout
app = pn.Column(
    text_input,
    plot_pane,
)

app.servable()

