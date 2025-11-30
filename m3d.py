import sys
sys.stdout.flush()

import os
os.environ["DEMO_USE"] = "panel"
os.environ["MATHICS3_TIMING"] = "-1"

import threading
import re

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

pn.extension('plotly')
pn.extension('mathjax')
#pn.extension(template="bootstrap")
pn.extension(raw_css=[open('assets/m3d.css').read()])

class FE:
    def __init__(self):
        self.session = core.MathicsSession()
        pass

fe = FE()

buttons = pn.Row(
    pn.widgets.ButtonIcon(icon="help"),
    pn.widgets.ButtonIcon(icon="file-download"),
    pn.widgets.ButtonIcon(icon="file-upload"),
    pn.widgets.ButtonIcon(icon="edit"),
    pn.widgets.ButtonIcon(icon="player-play"),
    pn.widgets.ButtonIcon(icon="clipboard-text"),
    pn.widgets.ButtonIcon(icon="mood-smile"),
    pn.widgets.ButtonIcon(icon="mood-confuzed"),
    pn.widgets.ButtonIcon(icon="alert-triangle"),
    pn.widgets.ButtonIcon(icon="square-x"),
    #pn.widgets.ButtonIcon(icon="heart"),
    #pn.widgets.ButtonIcon(icon="file-pencil"),    
    #pn.widgets.ButtonIcon(icon="player-track-next"),
    css_classes=["m3d-button-bar"]
)

app = pn.Column(
    buttons,
    css_classes=["m3d-app"]
)

def load():
    md_fn = sys.argv[1] if len(sys.argv) > 1 else "gallery.m3d"
    print("loading", md_fn)
    md_str = open(md_fn).read()
    md_parts = re.split("(```)", md_str)
    is_m3 = False
    for part in md_parts:
        if part == "```":
            is_m3 = not is_m3
        elif is_m3:
            expr = fe.session.parse(part)
            print(expr)
            layout = lt.expression_to_layout(fe, expr)
            app.append(layout)
        else:
            #help(pn.pane.Markdown)
            md = pn.pane.Markdown(
                part,
                disable_math = False,
                css_classes=["m3d-markdown"],
                stylesheets=["""
                    * {
                        font-family: sans-serif;
                        font-size: 12pt;
                    }
                    h1 {font-size: 20pt;}
                    h2 {font-size: 18pt;}
                    h3 {font-size: 16pt;}
                    h4 {font-size: 24pt;}
                """]
            )
            print("appending md", md)
            app.append(md)



if "DEMO_BUILD_PYODIDE" in os.environ:
    # building
    print("building")
    app.servable()
elif "pyodide" in sys.modules:
    # running under pyodide
    print("running under pyodide")
    load()
    app.servable()
else:
    print("running as local server")
    load()
    pn.serve(app, port=9999, address="localhost", threaded=True, show=False) 
    time.sleep(1)
    util.Browser().show("http://localhost:9999").start()
