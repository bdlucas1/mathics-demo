import os
os.environ["DEMO_USE"] = "panel"
os.environ["MATHICS3_TIMING"] = "-1"

import threading

import panel as pn
import panel.widgets as pnw
import plotly.express as px
import plotly.graph_objects as go
import param

import core
import sym
import layout as lt
import os
import util
import hook
import sys
import time
import mode

#pn.extension('ipywidgets')
pn.extension('plotly')
pn.extension('mathjax')


# start mathics session
#expr = session.parse("Plot3D[Cos[x] Sin[y], {x,0,4 Pi}, {y,0, 6 Pi}]")
#expr = expr.evaluate(session.evaluation)

class FE:

    def __init__(self):
        self.session = core.MathicsSession()
        pass

fe = FE()

#help(pn.widgets.TextAreaInput)

class Pair(pn.Column):

    def __init__(self, text=None):
        
        self.old_expr = ""

        # input
        instructions = "Type expression followed by shift-enter"
        self.input = pn.widgets.TextAreaInput(
            placeholder = instructions,
            value = text,
            value_input = text,
            auto_grow = True,
            max_rows = 9999,
            #sizing_mode = "stretch_width",
            css_classes = ["m-input"]
        )

        # output
        self.output = pn.Column(css_classes = ["m-output"])

        super().__init__(self.input, self.output, css_classes=["m-pair"])

        self.update_if_changed(force=True)

    # check whether input has changed, and eval if so
    def update_if_changed(self, force=False):
        expr = self.input.value_input
        if expr and (force or expr != self.old_expr):
            self.old_expr = expr
            expr = fe.session.parse(expr)
            expr = expr.evaluate(fe.session.evaluation)
            layout = lt.expression_to_layout(fe, expr)
            self[1] = layout

pairs = pn.Column(css_classes=["m-pairs"])

def update_changed(force=False):
    for pair in pairs:
        pair.update_if_changed(force=force)

shortcuts = mode.KeyboardShortcuts(shortcuts=[
    mode.KeyboardShortcut(name="run", key="Enter", ctrlKey=True),
    mode.KeyboardShortcut(name="run", key="Enter", altKey=True),
    mode.KeyboardShortcut(name="run", key="Enter", metaKey=True),
    mode.KeyboardShortcut(name="run_force", key="Enter", ctrlKey=True, shiftKey=True),
    mode.KeyboardShortcut(name="run_force", key="Enter", altKey=True, shiftKey=True),
    mode.KeyboardShortcut(name="run_force", key="Enter", metaKey=True, shiftKey=True),
])

def shortcut_msg(event):
    if event.data == "run":
        update_changed()
    if event.data == "run_force":
        update_changed(force=True)
shortcuts.on_msg(shortcut_msg)

app = pn.Feed(pairs, shortcuts, view_latest=True, css_classes=["m-top"])
app.servable()
