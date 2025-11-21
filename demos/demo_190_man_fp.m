Manipulate[
    Plot3D[
        FractionalPart[x y],
        {x,-l,l}, {y,-l,l},
        PlotPoints->{200,200}
    ],
    {{l,1.5},0.95,2,0.05}
]
