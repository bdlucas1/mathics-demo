(*
DensityPlot[
   Sin[x^2+y^2] / Sqrt[x^2+y^2+1], {x,-3,3}, {y,-3,3},
   PlotPoints -> {20,20}
]
 *)

DensityPlot[
   x+y, {x,0,1}, {y,0,1},
   PlotPoints -> {2,2}(*,
   Mesh->Full*)
]

