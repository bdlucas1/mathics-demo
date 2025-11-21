Manipulate[
    Plot3D[
        {-Abs[Exp[Exp[x + I y]]], -1}, {x,-xlim,xlim}, {y,-ylim,ylim},
        PlotPoints->{200,200},
        PlotRange->{Automatic, Automatic, {-zlim,2}}
    ],
    {{xlim,1.5}, 1, 2, 0.05},
    {{ylim,6}, 1, 10, 0.1},
    {{zlim,10}, 1, 50, 1}
]
