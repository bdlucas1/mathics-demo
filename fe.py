import argparse
import re
import threading
import traceback
import webbrowser

import webview
import werkzeug

import graphics
import mcs
import mode
import util

#
#
#

parser = argparse.ArgumentParser(description="Graphics demo")
parser.add_argument("--fe", choices=["shell", "browser", "jupyter"], default="shell")
parser.add_argument("--browser", choices=["webview", "webbrowser"], default="webview")
parser.add_argument("--run", choices=["demos","tests","timing","dev"], default=None)
parser.add_argument("--dev", type=str, default=None)
parser.add_argument("demo", type=str, default=None, nargs="?")
args = parser.parse_args()

run = dict(

    demos = [
        "plot_sin",
        "plot_manipulate_sin",
        # TODO: System`Hypergeometric1F1 gets rewritten to varous functions involving gamma, bessel, etc.
        # need to build those out in compile.py to handle
        # for now just use Demo`Hypergeomtric which compile knows about but mathics evaluate doesn't
        "plot_manipulate_hypergeometric",
        "demo_row",
        "demo_grid",
        "jax",
        "mixed",
    ],

    tests = [
        "plot_sin_old_20",
        "plot_sin",
        "plot_manipulate_sin",
        "plot_manipulate_hypergeometric",
        "test_gc1",
        "test_gc2",
        "align",
    ],

    # run multiple times, take fastest
    timing = [
        #"plot_sin_old_200", "plot_sin_old_200",
        "plot_sin", "plot_sin", "plot_sin" ,
        #"plot_manipulate_sin", "plot_manipulate_sin", "plot_manipulate_sin",
        #"plot_manipulate_hypergeometric", "plot_manipulate_hypergeometric", "plot_manipulate_hypergeometric",
    ],
)

# process --run and --dev, read demo files
def read_demo(s):
    with open(f"demos/{s}.m") as f:
        return f.read()
if args.dev:    
    run["dev"] = [args.dev]
    args.run = "dev"
if args.demo:
    run["demo"] = [args.demo]
    args.run = "demo"
if args.run:
    run[args.run] = [read_demo(s) for s in run[args.run]]

# hack alert
if "ipy" in mode.use:
    import fe_ipy as fe
else:
    import fe_dash as fe
fe.args = args
fe.run = run
fe.browser = Browser()
front_end = fe.ShellFrontEnd if args.fe=="shell" else fe.BrowserFrontEnd
threading.Thread(target = front_end).start()
fe.browser.start()
