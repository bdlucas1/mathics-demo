import panel as pn

panel = pn.Row("foo")
panel.on_js_event("keydown", lambda: None)
panel.servable()
