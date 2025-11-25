import sys
import threading
import traceback

import dash
import werkzeug

import core
import layout as lt
import mode  # really just need mode_dash
import sym
import util

from mathics.eval.drawing.plot_compile import CompileError

# common to ShellFrontEnd and BrowserFrontEnd
class DashFrontEnd:

    # TODO: maybe remove jupyter flag as we are using ipywidgets, not dash in jupyter
    def __init__(self, jupyter=False):

        # create app, set options
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.app.enable_dev_tools(debug = mode.debug, dev_tools_silence_routes_logging = True) #not args.debug)
        self.jupyter = jupyter

        # TODO: I think this condition is always true now
        if not self.jupyter:
            # start server on its own thread, allowing something else to run on main thread
            # pass it self.app.server which is a Flask WSGI compliant app so could be hooked to
            # any WSGI compliant server
            # make_server picks a free port because we passed 0 as port number
            self.server = werkzeug.serving.make_server("127.0.0.1", 0, self.app.server)
            threading.Thread(target = self.server.serve_forever).start()
            print("using port", self.server.server_port)

        # everybody needs a Mathics session
        self.session = core.MathicsSession()

        # register pattern-matching callbacks for dymanically generated content, used by all front ends
        mode.register_callbacks(self.app)


# accept expressions from an input field, display expressions in an output box
class BrowserFrontEnd(DashFrontEnd):

    def __init__(self):

        # initialize app and start server
        super().__init__()

        # initial layout is --run input plus a blank pair
        self.pair_number = 0
        self.top_id ="browser-front-end"

        init_pairs = []
        for fn in sys.argv[1:]:

            if fn in util.methods:
                util.switch_method(fn)
                continue

            print("===", fn)
            s = open(fn).read()
            output = self.process_input(s)
            s = f"(* {fn} *)\n" + s
            pair = self.pair(s, output)
            init_pairs.append(pair)

        self.app.layout = dash.html.Div([*init_pairs, self.pair()], id=self.top_id)

        # when the hidden pair-button is "clicked", process the pair-in input and update the pair-out div
        @self.app.callback(
            dash.Output(dict(type="pair-out", pair_number=dash.MATCH), "children"),
            dash.Input(dict(type="pair-button", pair_number=dash.MATCH), "n_clicks"),
            dash.State(dict(type="pair-in", pair_number=dash.MATCH), "value"),
            prevent_initial_call = True
        )
        def update_pair_output(_, input_value):
            return self.process_input(input_value)

        # when any pair-out changes, if it's the last pair, append a new fresh pair to self.top_id
        @self.app.callback(
            dash.Output(self.top_id, "children"),
            dash.Input(dict(type="pair-out", pair_number=dash.ALL), "children"),
            prevent_initial_call = True
        )
        def append_new_pair(_):
            if dash.ctx.triggered_id and dash.ctx.triggered_id["pair_number"] == self.pair_number:
                patch = dash.Patch()
                patch.append(self.pair())
                return patch
            raise dash.exceptions.PreventUpdate
            
        # point a browser at our page
        if self.jupyter:
            self.app.run(jupyter_mode="inline")
        else:
            url = f"http://127.0.0.1:{self.server.server_port}"
            browser.show(url)
            

    def process_input(self, s):

        result = None

        from mathics_scanner.errors import InvalidSyntaxError

        with util.Timer(f"total parse+eval+layout"):
            try:
                expr = self.session.parse(s)
                if expr:
                    expr = expr.evaluate(self.session.evaluation)
                    result = lt.expression_to_layout(self, expr)
            except InvalidSyntaxError as oops:
                # uggh
                start, stop = [int(x) for x in str(oops)[1:-1].split(",")]
                print("xxx start stop", start, stop)
                result = f"syntax error {str(oops)}:\n" + s[:start] + ">>>" +  s[start:stop] + "<<<" + s[stop:]
            except CompileError as oops:
                result = str(oops)
            except Exception as oops:
                result = str(oops)
                util.print_exc_reversed()

        # text output
        if not result:
            if getattr(expr, "head", None) in set([sym.SymbolGraphics, sym.SymbolGraphics3D]):
                result = str(expr.head)
            else:
                # TODO: how to get this to output Sin instead of System`Sin etc.
                result = str(expr)

        return result

    # creates a layout for an input field and an output div
    # optionally pre-populates the output div (used for the demos - otherwise output starts out empty)
    def pair(self, input="", output=None):

        self.pair_number += 1
        pair_id = f"pair-{self.pair_number}"
        in_id =     dict(type="pair-in",     pair_number=self.pair_number)
        button_id = dict(type="pair-button", pair_number=self.pair_number)
        out_id =    dict(type="pair-out",    pair_number=self.pair_number)

        # create an input field, a div to hold output, a hidden button, and a number label
        # that is used to signal that the user has pressed shift-enter
        # TODO: can we get rid of hidden button by making tweak_pair more sophisticated?
        instructions = "Type expression followed by shift-enter"
        layout = dash.html.Div([
            dash.dcc.Textarea(
                id=in_id,
                value=input.strip(),
                placeholder=instructions,
                spellCheck=False,
                className="m-input"
            ),
            dash.html.Button(id=button_id, hidden=True),
            dash.html.Div(output, id=out_id, className="m-output"),
            dash.html.Div(str(self.pair_number), className="m-number"),
            # run tweak_pair (from assets/tweaks.js) to tweak the behavior of the pair:
            #    shift-enter in textarea clicks the button
            #    resize textarea height on every input
            mode.exec_js(f"tweak_pair('{pair_id}')"),

        ], id=pair_id, className="m-pair")

        return layout

if __name__ == "__main__":

    browser = util.Browser()
    threading.Thread(target = BrowserFrontEnd).start()
    browser.start()
