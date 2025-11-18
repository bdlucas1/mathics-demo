import plotly.graph_objects as go
import util

# compute axis options
def axis(show, range, title):
    axis = dict(showspikes=False, ticks="outside", range=range, title=title, linecolor="black")
    if not show:
        axis |= dict(visible=False, showline=False, ticks=None, showticklabels=False)
    return axis

class Thing:

    def __init__(self, fe, dim, options):
        self.fe = fe
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
    def add_mesh(self, vertices, polys):

        # TODO: 2d case, e.g. DensityPlot?
        if self.dim==3:
            mesh = go.Mesh3d(
                x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                i=polys[:,0], j=polys[:,1], k=polys[:,2],
                # TODO: hmm, colorscale is figure-level, isn't it?
                showscale=self.options.showscale,
                colorscale=self.options.colorscale,
                colorbar=dict(thickness=10), intensity=vertices[:,2],
                hoverinfo="none"
            )
        elif self.dim==2:
            # this is hacky because
            # 1) names are funky given indexing - rename
            # 2) use of points to approximate mesh
            # 2a) at least choose a good size and shape for the points that works for square mesh
            # 3) use centroid, probably
            # 4) use colors
            # 5) apply the indexing thing elsewhere too
            # 6) vertices are being generated but here we have to un-generate
            #    make generation of vertices and ungeneration specific to each plot type
            # 7) Timer for DensityPlot
            # 8) it came in as quads, keep it that way - move triangulation inside
            # 9) enough diffs that we should probably have Thing2 and Thing3
            # 10) rename THing
            # 11) why no axes?
            # 12) no colors!
            print("xxx", type(vertices), type(polys))
            if vertices is not None:
                points = vertices[polys]
            else:
                points = polys
            points = points.reshape(-1, 2) # should take centroid of each poly
            print("xxx", points)
            mesh = go.Scatter(
                x=points[:,0], y=points[:,1],
                mode='markers', marker=dict(color='black', size=8)
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
            if hasattr(self.fe, "test_image"):
                import plotly.io as pio
                pio.write_image(figure, self.fe.test_image)
                print("wrote", self.fe.test_image)

        return figure

