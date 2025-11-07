# TODO: reconstitute this

# read expressions from terminal, display results in a browser winddow
class ShellFrontEnd(DashFrontEnd):

    def __init__(self):

        # initialize app and start server
        super().__init__()

        # map from plot names to plot layouts, one per plot
        self.plots = {}

        # initial layout is empty save for a Location component
        # which causes the desired plot to be displayed as detailed below
        self.app.layout = dash.html.Div([dash.dcc.Location(id="url")], id="shell-front-end")

        # to display plot x browser is instructed to fetch url with path /plotx 
        # when browser fetches /plotx, it is served the initial (empty) layout defined above
        # then the dcc.Location component in that layout triggers this callback,
        # which receives the path /plotx of the loaded url
        # and updates the shell-front-end div of the initial (empty) layout with the actual layout for /plotx
        @self.app.callback(
            dash.Output("shell-front-end", "children"), # we update the shell-front-end layout with the layout for plot x
            dash.Input("url", "pathname")            # we receive the url path /plotx
        )
        def layout_for_path(path):
            # returning this value updates shell-front-end div with layout for plotx
            return self.plots[path[1:]]

        def handle_input(s):

            layout = None

            with util.Timer(f"total parse+eval+layout"):
                try:
                    expr = self.session.parse(s)
                    if expr:
                        expr = expr.evaluate(self.session.evaluation)
                        layout = lt.expression_to_layout(self, expr)
                except Exception as e:
                    if True: #args.run == "dev" or mode.debug:
                        traceback.print_exc()
                    else:
                        print("ERROR:", e)

            # graphicical output, if any
            if layout:
                plot_name = f"plot{len(self.plots)}"
                self.plots[plot_name] = layout
                url = f"http://127.0.0.1:{self.server.server_port}/{plot_name}"
                browser.show(url)
                text_output = "--Graphics--"
            else:
                text_output = str(expr)
            print(f"\noutput> {text_output}")

        # demos, tests, etc.
        if args.run:
            for s in run[args.run]:
                print("input> ", s)
                handle_input(s)
                print("")

        # REPL loop
        while True:
            print("input> ", end="")
            s = input()
            handle_input(s)
            print("")


