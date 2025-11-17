import plotly.graph_objects as go
import util

# compute axis options
def axis(show, range, title):
    axis = dict(showspikes=False, ticks="outside", range=range, title=title, linecolor="black")
    if not show:
        axis |= dict(visible=False, showline=False, ticks=None, showticklabels=False)
    return axis

class Thing:

    def __init__(self, dim, options):
        self.dim = dim
        self.data = []
        self.options = options

    util.Timer("add_points")
    def add_points(self, vertices, points):
        
        scatter_points = go.Scatter(
            x = points[:,0], y = points[:,1],
            mode='markers', marker=dict(color='black', size=8)
        )
        #figure.add_trace(scatter_points)
        self.data.append(scatter_points)

    util.Timer("add_lines")
    def add_lines(self, vertices, lines):
        for line in lines:
            scatter_lines = go.Scatter(
                x = line[:,0], y = line[:,1],
                mode='lines', line=dict(color='black', width=1)
            )
            #figure.add_trace(scatter_lines)
            self.data.append(scatter_lines)

    # TODO: move triangulation inside?
    util.Timer("add_mesh")
    def add_mesh(self, xyzs, ijks):

        # TODO: 2d case, e.g. DensityPlot?
        mesh = go.Mesh3d(
            x=xyzs[:,0], y=xyzs[:,1], z=xyzs[:,2],
            i=ijks[:,0], j=ijks[:,1], k=ijks[:,2],
            # TODO: hmm, colorscale is figure-level, isn't it?
            showscale=self.options.showscale,
            colorscale=self.options.colorscale,
            colorbar=dict(thickness=10), intensity=xyzs[:,2],
            hoverinfo="none"
        )
        self.data.append(mesh)

    util.Timer("figure")
    def figure(self):

        if self.dim == 2:
            layout = go.Layout(
                margin = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                width=self.options.width,
                height=self.options.height,
                xaxis = axis(self.options.axes[0], self.options.x_range, None),
                yaxis = axis(self.options.axes[1], self.options.y_range, None),
            )

        elif self.dim == 3:
            layout = go.Layout(
                margin = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                width=self.options.width,
                height=self.options.height,
                scene = dict(
                    xaxis = axis(self.options.axes[0], range=self.options.x_range, title="x"),
                    yaxis = axis(self.options.axes[1], range=self.options.y_range, title="y"),
                    zaxis = axis(self.options.axes[2], range=self.options.z_range, title="z"),
                    aspectmode="cube",
                )
            )

        with util.Timer("FigureWidget"):
            figure = go.FigureWidget(data=self.data, layout = layout)

        return figure


"""
@util.Timer("plot2d")
def plot2d(lines, points, options: Options):

    data = []

    # add points
    if points is not None and len(points):
        with util.Timer("scatter points"):
            scatter_points = go.Scatter(
                x = points[:,0], y = points[:,1],
                mode='markers', marker=dict(color='black', size=8)
            )
            #figure.add_trace(scatter_points)
            data.append(scatter_points)

    # add lines
    if lines is not None and len(lines):
        with util.Timer("scatter lines"):
            for line in lines:
                scatter_lines = go.Scatter(
                    x = line[:,0], y = line[:,1],
                    mode='lines', line=dict(color='black', width=1)
                )
                #figure.add_trace(scatter_lines)
                data.append(scatter_lines)

    # plot layout
    layout = go.Layout(
        margin = dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        width=options.width,
        height=options.height,
        xaxis = axis(options.axes[0], options.x_range, None),
        yaxis = axis(options.axes[1], options.y_range, None),
    )

    with util.Timer("FigureWidget"):
        figure = go.FigureWidget(data=data, layout = layout)

    return figure
"""

"""
@util.Timer("plot3d")
def plot3d(xyzs, ijks, lines, points, options):

    data = []

    # add mesh from xyzs, ijks
    with util.Timer("mesh"):
        mesh = go.Mesh3d(
            x=xyzs[:,0], y=xyzs[:,1], z=xyzs[:,2],
            i=ijks[:,0], j=ijks[:,1], k=ijks[:,2],
            showscale=options.showscale, colorscale=options.colorscale, colorbar=dict(thickness=10), intensity=xyzs[:,2],
            hoverinfo="none"
        )
        data.append(mesh)

    # TODO: points
    # TODO: lines

    # plot layout
    layout = go.Layout(
        margin = dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        width=options.width,
        height=options.height,
        scene = dict(
            xaxis = axis(options.axes[0], range=options.x_range, title="x"),
            yaxis = axis(options.axes[1], range=options.y_range, title="y"),
            zaxis = axis(options.axes[2], range=options.z_range, title="z"),
            aspectmode="cube",
        )
    )

    # TODO: supposedly using add_trace later instead of data=[mesh] should work.
    # It did with dash and with ipywigets in jupyterlab, not did not in with ipywidgets in voila.
    with util.Timer("FigureWidget"):
        figure = go.FigureWidget(data=mesh, layout = layout)

    return figure
"""
