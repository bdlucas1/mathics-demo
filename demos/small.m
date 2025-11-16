(*
Plot3D[
   Sin[x^2+y^2] / Sqrt[x^2+y^2+1], {x,-3,3}, {y,-3,3},
   PlotPoints -> {20,20}, ColorFunction->"viridis", PlotLegends->BarLegend["viridis"]
]
 *)

Plot3D[
   Sin[x^2+y^2] / Sqrt[x^2+y^2+1], {x,-3,3}, {y,-3,3},
   PlotPoints -> {2,2}, MaxRecursion->0, ColorFunction->"viridis", PlotLegends->BarLegend["viridis"]
]
