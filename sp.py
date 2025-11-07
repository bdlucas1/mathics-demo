import sympy
import numpy
import scipy

x = sympy.Symbol("x")
y = sympy.Symbol("y")
z = sympy.Symbol("z")
a = sympy.Symbol("a")
b = sympy.Symbol("b")

a1 = numpy.array([1,2])
a2 = numpy.array([2,1])

expr1 = sympy.sin(x)
fun1 = sympy.lambdify(x, expr1, "numpy")
val1 = fun1(a1)
print(fun1(a1))

expr2 = sympy.sin(x) + x**2
fun2 = sympy.lambdify(x, expr2, "numpy")
val2 = fun2(a1)
print(val2)

expr3 = x > y
fun3 = sympy.lambdify((x, y), expr3, "numpy")
val3 = fun3(a1, a2)
print(val3)

def hyppfq(p, q, x):
    if len(p) == 1 and len(q) == 1:
        return scipy.special.hyp1f1(p[0], q[0], x)
    else:
        raise Exception(f"can't handle hyppfq({p}, {q}, x)")

expr4 = sympy.hyper([a], [b], z)
fun4 = sympy.lambdify((a, b, z), expr4, [{"hyper": hyppfq}, "numpy"])
val4 = fun4(1, 2, 1)
print(val4)
