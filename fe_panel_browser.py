import threading
import sys
import time

import panel as pn

import util
from fe_panel_app import app, pairs, Pair

import pandas

# initial files from command line
def initial_pairs():
    time.sleep(1)
    for fn in sys.argv[1:]:
        time.sleep(0.1)
        print("=== processing", fn)
        with open(fn) as f:
            expr = f.read()
            expr = f"(* {fn.split("/")[-1]} *)\n" + expr
            pair = Pair(expr)
            pairs.append(pair)
    pairs.append(Pair())
threading.Thread(target=initial_pairs).start()
#initial_pairs()
        
server = pn.serve(app, port=9999, address="localhost", threaded=True, show=False) 
time.sleep(1)
util.Browser().show("http://localhost:9999").start()

