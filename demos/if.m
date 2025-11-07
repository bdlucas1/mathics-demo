Plot3D[
    If[x > y, 1, -1], {x,-3,3}, {y,-3,3},
    PlotPoints -> {200,200}, ColorFunction->"viridis", PlotLegends->BarLegend["viridis"]
]
