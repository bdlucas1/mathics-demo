Manipulate[
    Plot3D[
        {Exp[Exp[x + I y]], 1},
        {x,-xlim,xlim}, {y,-ylim,ylim},
        PlotRange->{Automatic, Automatic, {-2,zlim}},
        BoxRatios->{1,1,1}
    ],
    {{xlim,1.5}, 1, 2, 0.05},
    {{ylim,6}, 1, 10, 0.1},
    {{zlim,10}, 1, 50, 1}
]
