from fe_panel_app import app

import time
import util
import panel as pn

print("xxx serving")
server = pn.serve(app, port=9999, address="localhost", threaded=True, show=False) 
time.sleep(1)
util.Browser().show("http://localhost:9999").start()

