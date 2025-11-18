import scipy
import sympy

import mcs
import util


def hyppfq(p, q, x):
    if len(p) == 1 and len(q) == 1:
        return scipy.special.hyp1f1(p[0], q[0], x)
    else:
        raise Exception(f"can't handle hyppfq({p}, {q}, x)")

# mappings for sympy functions that aren't handled by
# the default mapping to numpy
additional_mappings = {
    "hyper": hyppfq
}

def compile(evaluation, functions, names):

    print("=== compiling expr"); util.prt_expr_tree(functions)

    # obtain sympy expr and strip context from free symbols
    sympy_expr = functions.to_sympy()
    subs = {sym: sympy.Symbol(mcs.strip_context(str(sym))) for sym in sympy_expr.free_symbols}
    sympy_expr = sympy_expr.subs(subs)

    print("=== compiled sympy", type(sympy_expr)); util.prt_sympy_tree(sympy_expr)

    # ask sympy to generate a function that will evaluate the expr
    # use numpy to do the evaluation so that operations are vectorized
    # augment the default numpy mappings with some additional ones not handled by default
    fun = sympy.lambdify(sympy.symbols(names), sympy_expr, [additional_mappings, "numpy"])

    return fun
