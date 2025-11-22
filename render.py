import numpy as np
import plotly.graph_objects as go

import util


# TODO: move to consumer
def need_vertices(vertices, items):
    if vertices is None:
        with util.Timer("make vertices"):
            vertices = items.reshape(-1, items.shape[-1])
            items = np.arange(len(vertices)).reshape(items.shape[:-1])
    return vertices, items

class FigureBuilder:

    # options are graphics_options
    def __init__(self, dim, fe, options):
        self.fe = fe
        self.dim = dim
        self.data = []
        self.options = options

    util.Timer("add_points")
    def add_points(self, vertices, points):
        if vertices is not None:
            lines = vertices[lines]
        if self.dim == 2:
            scatter_points = go.Scatter(
                x = points[:,0], y = points[:,1],
                mode='markers', marker=dict(color='black', size=8)
            )
        elif self.dim == 3:
            # TODO: not tested
            scatter_points = go.Scatter3D(
                x = points[:,0], y = points[:,1], z = points[:,2],
                mode='markers', marker=dict(color='black', size=8)
            )
        self.data.append(scatter_points)

    util.Timer("add_lines")
    def add_lines(self, vertices, lines):
        if vertices is not None:
            lines = vertices[lines]
        for line in lines:
            if self.dim == 2:
                scatter_line = go.Scatter(
                    x = line[:,0], y = line[:,1],
                    mode='lines', line=dict(color='black', width=1),
                    showlegend=False
                )
            elif self.dim == 3:
                scatter_line = go.Scatter3d(
                    x = line[:,0], y = line[:,1], z = line[:,2],
                    mode='lines', line=dict(color='black', width=1),
                    showlegend=False
                )
            self.data.append(scatter_line)

    # TODO: move triangulation inside?
    util.Timer("add_mesh")
    def add_polys(self, vertices, polys):

        if self.dim==3:

            vertices, polys = need_vertices(vertices, polys)


            with util.Timer("triangulate"):
                ijks = []
                ngon = polys.shape[1]
                for i in range(1, ngon-1):
                    inx = [0, i, i+1]
                    tris = polys[:, inx]
                    ijks.extend(tris)
                ijks = np.array(ijks)

            mesh = go.Mesh3d(
                x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                i=ijks[:,0], j=ijks[:,1], k=ijks[:,2],
                # TODO: hmm, colorscale is figure-level, isn't it?
                showscale=self.options.showscale,
                colorscale=self.options.colorscale,
                colorbar=dict(thickness=10), intensity=vertices[:,2],
                hoverinfo="none"
            )

        elif self.dim==2:
            # this is hacky because
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
            if vertices is not None:
                points = vertices[polys]
            else:
                points = polys
            points = points.reshape(-1, 2) # should take centroid of each poly
            mesh = go.Scatter(
                x=points[:,0], y=points[:,1],
                mode='markers', marker=dict(color='black', size=8)
            )

        self.data.append(mesh)

    @util.Timer("figure")
    def figure(self):

        with util.Timer("data_range"):
            if self.dim == 3:
                data = np.hstack([(trace.x, trace.y, trace.z) for trace in self.data])
            else:
                data = np.hstack([(trace.x, trace.y) for trace in self.data])
            data_range = np.array([data.min(axis=1), data.max(axis=1)]).T

        #padding = (data_range[:,1] - data_range[:,0]) * 0.05
        #plot-range = np.array([data_range[:,0] - padding, data_range[:,1] + padding]).T

        plot_range = [s if s is not None else d for s, d in zip(self.options.plot_range, data_range)]

        # TODO: make consistent with dim==3
        def axis(show, range, title):
            axis = dict(showspikes=False, ticks="outside", range=range, title=title, linecolor="black")
            if not show:
                axis |= dict(visible=False, showline=False, ticks=None, showticklabels=False)
            return axis

        if self.dim == 2:
            layout = go.Layout(
                margin = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                width=self.options.image_size[0],
                height=self.options.image_size[1],
                xaxis = axis(self.options.axes[0], plot_range[0], None),
                yaxis = axis(self.options.axes[1], plot_range[1], None),
            )

        elif self.dim == 3:

            scene = dict(aspectmode="cube")

            if self.options.boxed:
                vertices = np.array(np.meshgrid(*plot_range)).reshape((3,-1)).T
                lines = [(i, i^k) for i in range(8) for k in [1,2,4] if not i&k]
                self.add_lines(vertices, lines)

            for i, p in enumerate("xyz"):
                scene[p+"axis"] = dict(
                    visible = self.options.axes[i],
                    range = plot_range[i],
                    showbackground = False,
                    title = p,
                    showline = True,
                    linecolor = "black",
                    linewidth = 1,
                    showspikes=False,
                    ticks="outside",
                )
            layout = go.Layout(
                margin = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                width=self.options.image_size[0],
                height=self.options.image_size[1],
                scene = scene
            )

        with util.Timer("FigureWidget"):
            figure = go.FigureWidget(data=self.data, layout = layout)
            if hasattr(self.fe, "test_image"):
                import plotly.io as pio
                pio.write_image(figure, self.fe.test_image)
                print("wrote", self.fe.test_image)

        return figure

