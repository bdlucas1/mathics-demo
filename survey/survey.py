import sym
import core
import tabbed
import util

session = core.MathicsSession()


def read(fn):
    f = open(fn)
    return {d["option"]: d for d in tabbed.read(f)}

def nc(s):
    return str(s).split("`")[-1]

def get_options(expr):
    options = {}
    for e in expr.elements:
        if hasattr(e, "head") and e.head == sym.SymbolRule:
            option = nc(e.elements[0])
            options[option] = nc(e.elements[1])
    return options

def survey_plot3D():

    plot3d = read("wma-plot3d.tab")
    graphics3d = read("wma-graphics3d.tab")

    def eval_plot(*option_pairs):

        option_tuples = zip(option_pairs[0::2], option_pairs[1::2])
        options_str = ", ".join(f"{option} -> {value}" for option, value in option_tuples)
        options_str = ", " + options_str if options_str else ""
        expr_str = f"Plot3D[1, {{x,0,1}}, {{y,0,1}}{options_str}]"
        print(expr_str)

        try:
            expr = session.parse(expr_str)
        except Exception as oops:
            print(f"{expr_str}: {oops}")
            exit(-1)

        result = expr.evaluate(session.evaluation)
        return result


    result = eval_plot("Boxed", "False")
    #print(result)
    options = get_options(result)
    print(options.keys())

    return




    for option, info in plot3d.items():

        #NEXT: do with no args
        #compare result/expected
        #create merged table
        #record status
        #we are supplying some values - is that ok???

        if info.bad:
            print("===", option)
            result = eval_plot(option, info.bad)
            result_options = get_options(result)
            for option, value in result_options.items():
                expected = (plot3d.get(option) or graphics3d.get(option)).default
                print(option, expected==value, expected, value)



survey_plot3D()
