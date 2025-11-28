import os
os.environ["DEMO_USE"] = "panel"
os.environ["MATHICS3_TIMING"] = "-1"

import panel as pn
import panel.widgets as pnw
import plotly.express as px
import plotly.graph_objects as go
#import ipywidgets as ipw

import core
import sym
import layout as lt
import os
import util
import hook
import sys
import time

#pn.extension('ipywidgets')
pn.extension('plotly')

# start mathics session
#expr = session.parse("Plot3D[Cos[x] Sin[y], {x,0,4 Pi}, {y,0, 6 Pi}]")
#expr = expr.evaluate(session.evaluation)

class FE:

    def __init__(self):
        self.session = core.MathicsSession()
        pass

fe = FE()

class Pair:

    def __init__(self, text=None):
        
        # input
        self.text_input = pn.widgets.TextInput(
            placeholder = "Enter expression",
            value = text
        )

        # output
        #self.output_pane = pn.pane.IPyWidget(ipw.HBox(), height=400)
        self.output_pane = pn.Column()

        # parse and eval expr, and display it in output_pane
        def process_input(expr):
            expr = fe.session.parse(expr)
            expr = expr.evaluate(fe.session.evaluation)
            layout = lt.expression_to_layout(fe, expr)
            print("xxx layout", layout)
            #self.output_pane[0] = layout
            self.pair[1] = pn.Column(layout)

        # receive input and update output
        def update_plot(event):
            expr = self.text_input.value
            process_input(expr)
        self.text_input.param.watch(update_plot, "value")

        # bundle them
        self.pair = pn.Column(self.text_input, self.output_pane)

        # process initial text
        if text:
            process_input(text)



app = pn.Column()

if __name__ == "__main__":

    # initial files from command line
    for fn in sys.argv[1:]:
        with open(fn) as f:
            expr = f.read()
        pair = Pair(expr)
        app.append(pair.pair)

    #app.show(port=9999)

if len(app) == 0:
    app.append(Pair().pair)

app.servable()
