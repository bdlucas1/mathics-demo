import os
import sys
import time
import traceback
import urllib.parse
import webbrowser
import webview

import mcs


def print_stack_reversed(file=None):
    """Print the current stack trace, from innermost to outermost."""
    if file is None:
        file = sys.stderr
    stack = traceback.extract_stack()
    for frame in reversed(stack):
        print(f'  File "{frame.filename}", line {frame.lineno}, in {frame.name}', file=file)
        if frame.line:
            print(f'    {frame.line.strip()}', file=file)            

def print_exc_reversed(exc_info=None, file=None):
    """Like traceback.print_exc(), but prints traceback frames in reverse order (innermost to outermost)."""
    if exc_info is None:
        exc_info = sys.exc_info()
    if file is None:
        file = sys.stderr

    etype, value, tb = exc_info
    if tb is None:
        print("No active exception", file=file)
        return

    stack = traceback.extract_tb(tb)
    print("Traceback (most recent call last, reversed):", file=file)
    for frame in reversed(stack):
        print(f'  File "{frame.filename}", line {frame.lineno}, in {frame.name}', file=file)
        if frame.line:
            print(f'    {frame.line.strip()}', file=file)
    print(f"{etype.__name__}: {value}", file=file)


#
# print expr as a tree
#

def prt_expr_tree(expr, indent=1):
    if not hasattr(expr, "elements"):
        print("  " * indent + str(expr))
    else:
        print("  " * indent + str(expr.head))
        for elt in expr.elements:
            prt_expr_tree(elt, indent + 1)

def prt_sympy_tree(expr, indent=""):
    if expr.args:
        print(f"{indent}{expr.func.__name__}")
        for i, arg in enumerate(expr.args):
            prt_sympy_tree(arg, indent + "    ")
    else:
        print(f"{indent}{expr.func.__name__}({str(expr)})")


#
#
#

class Timer:

    """
    Times a block of code. Maybe be used as a decorator or as a context manager:

        # decorator
        @Timer(name):
        def f(...):
            ...

        # context manager
        with Timer(name):
            ...

    Timings are nested (in execution order), and the output prints the nested
    timings as an "upside-down" indented outline, with an outer level printed after
    all nested inner levels, supporting both detailed and summary timings.
    
    Timing.level controls how deeply nested timings are displayed:
    -1 all, 0 none, 1 only top level, etc.  Default is 0. Use MATHICS_TIMING
    environment variable to change.
    """

    level = int(os.getenv("MATHICS_TIMING", "0"))
    timers = []

    def __init__(self, name):
        self.name = name

    def __call__(self, fun):
        def timed_fun(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)
        return timed_fun

    def start(name):
        Timer.timers.append((name, time.time()))

    def stop():
        name, start = Timer.timers.pop()
        ms = (time.time() - start) * 1000
        if Timer.level < 0 or len(Timer.timers) < Timer.level:
            print(f"{'  '*len(Timer.timers)}{name}: {ms:.1f} ms")

    def __enter__(self):
        if self.name:
            Timer.start(self.name)

    def __exit__(self, *args):
        if self.name:
            Timer.stop()

# possibly override our local definition
if os.getenv("DEMO_USE_MATHICS", False):
    print("using mathics version of Timer")
    from mathics.core.util import Timer
else:
    print("using demo version of Timer")

#
#
#

def get_rules(expr):
    for e in expr.elements:
        if hasattr(e, "head") and e.head == mcs.SymbolRule:
            yield e

def get_rule_values(expr):
    for rule in get_rules(expr):
        yield rule.elements[0], rule.elements[1].to_python()


#
#
#

# load a url into a browser, using either:
# webview - pop up new standalone window using pywebview
# webbrowser - instruct system browser to open a new window
class Browser():

    def __init__(self):
        self.n = 0
        self.browser = os.getenv("DEMO_BROWSER", "webview")

    def show(self, url):
        # display a browser window that fetches the current plot
        #print("showing", url)
        if self.browser == "webview":
            offset = 50 * self.n
            self.n += 1
            webview.create_window(url, url, x=100+offset, y=100+offset, width=600, height=800)
        elif self.browser == "webbrowser":
            webbrowser.open_new(url)

    def start(self):

        if self.browser == "webview":
            # webview needs to run on main thread :( and blocks, so we start other things on their own thread
            # webview needs a window before we can call start() :(, so we make a hidden one
            # real windows will be provided later
            webview.create_window("hidden", hidden=True)
            webview.start()


