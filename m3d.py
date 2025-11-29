import os
os.environ["DEMO_USE"] = "panel"
os.environ["MATHICS3_TIMING"] = "-1"


import sys
import re
import panel as pn
import layout as lt

pn.extension(raw_css=[open('assets/m3d.css').read()])
pn.extension("mathjax")

# TODO: not really what we want,
# but ran into problems registring Manipulate otherwise...
from fe_panel_app import fe

with open(sys.argv[1]) as f:
    md_str = f.read()

app = pn.Column(css_classes=["m3d-app"])

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
            """]
        )
        print("appending md", md)
        app.append(md)

pn.serve(app, port=9999)

