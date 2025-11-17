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
        
        if self.dim == 2:
            scatter_points = go.Scatter(
                x = points[:,0], y = points[:,1],
                mode='markers', marker=dict(color='black', size=8)
            )
        elif self.dim == 3:
            scatter_points = go.Scatter(
                x = points[:,0], y = points[:,1], z = points[:,2],
                mode='markers', marker=dict(color='black', size=8)
            )
        self.data.append(scatter_points)

    util.Timer("add_lines")
    def add_lines(self, vertices, lines):

        for line in lines:
            if self.dim == 2:
                scatter_lines = go.Scatter(
                    x = line[:,0], y = line[:,1],
                    mode='lines', line=dict(color='black', width=1),
                    showlegend=False
                )
            elif self.dim == 3:
                scatter_lines = go.Scatter3d(
                    x = line[:,0], y = line[:,1], z = line[:,2],
                    mode='lines', line=dict(color='black', width=1),
                    showlegend=False
                )
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

