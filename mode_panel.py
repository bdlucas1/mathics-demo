import time
import panel as pn

import layout as lt
import mode
import util

# --- Load CSS (Panel way instead of IPython.display) -------------------------

try:
    with open("assets/app.css") as f:
        css = f.read()
except FileNotFoundError:
    with open("app.css") as f:
        css = f.read()

# Register CSS with Panel
pn.extension(raw_css=[css])


# --- Basic wrappers ----------------------------------------------------------

def wrap(s):
    """Replace ipw.Label(value=s)"""
    return pn.widgets.StaticText(value=s)


def latex(s):
    """Replace ipw.Label(value='$...$') with a LaTeX pane."""
    if isinstance(s, str):
        # Panel's LaTeX pane renders math, no need to add $...$ unless you want inline explicitly
        return pn.pane.LaTeX(s)
    return s


def row(ls):
    """
    Replace ipw.HBox with baseline alignment.
    Strings become StaticText widgets.
    """
    items = [pn.widgets.StaticText(value=l) if isinstance(l, str) else l for l in ls]
    # Panel doesn't have "align_items='baseline'" directly, but Row is the closest equivalent
    return pn.Row(*items)


# --- Grid layout -------------------------------------------------------------

def grid(grid_content):
    """
    Replace ipw.GridBox + HBox wrapper with Panel's GridBox.
    grid_content is a list of rows, each row a list of widgets/strings.
    """
    n_rows = len(grid_content)
    n_cols = max(len(r) for r in grid_content) if n_rows > 0 else 0

    # Flatten children and convert strings
    children = []
    for r in grid_content:
        for cell in r:
            if isinstance(cell, str):
                children.append(pn.widgets.StaticText(value=cell))
            else:
                children.append(cell)

    # Panel GridBox uses ncols; we can approximate the same behavior
    gb = pn.GridBox(
        *children,
        ncols=n_cols,
        sizing_mode="fixed",  # helps avoid over-expanding horizontally
    )
    gb.css_classes = ["m-grid"]

    # Wrap in a Row (similar to ipw.HBox) to keep width under control
    layout = pn.Row(gb)
    return layout


# --- Graph layout (Plotly, etc.) --------------------------------------------

def graph(figure, height):
    """
    Replace ipw.HBox + spacer with Panel Plotly pane.
    Expects `figure` to be a Plotly figure or similar.
    """
    # Turn off the mode bar like your original code did
    plot = pn.pane.Plotly(figure, config={"displayModeBar": False}, height=int(height))

    # Spacer to roughly reproduce the baseline centering trick
    center_baseline = pn.Spacer(width=0, height=int(height / 2))

    layout = pn.Row(center_baseline, plot)
    return layout


# --- Manipulate (sliders + target layout) ------------------------------------

last_slider_update = None

def manipulate(init_target_layout, sliders, eval_and_layout):
    """
    Panel version of `manipulate`:

    - `init_target_layout`: initial Panel layout (or anything Panel can panelize)
    - `sliders`: iterable of objects with attrs: name, lo, hi, step, init
    - `eval_and_layout(values)`: function taking list of slider values and
      returning a new layout (Panel object) to replace the target.
    """

    # We'll create Panel FloatSliders for each descriptor
    pn_sliders = []

    def recompute(event=None):
        global last_slider_update

        if last_slider_update:
            # same place you had timing; uncomment if you want the print
            # print(f"between slider updates: {(time.time()-last_slider_update)*1000:.1f}")
            pass

        with util.Timer("slider update"):
            # Get current slider values
            values = [s.value for s in pn_sliders]
            target_layout = eval_and_layout(values)
            # Replace the contents of the target container
            target[:] = [target_layout]

        last_slider_update = time.time()

    # Build sliders
    for s in sliders:
        slider = pn.widgets.FloatSlider(
            name=s.name,
            start=s.lo,
            end=s.hi,
            step=s.step / 10,
            value=s.init,
            width_policy="max",  # similar to layout=ipw.Layout(width="100%")
        )
        # Watch changes to "value"
        slider.param.watch(recompute, "value")
        pn_sliders.append(slider)

    slider_box = pn.Column(*pn_sliders)
    slider_box.css_classes = ["m-sliders"]

    # Target layout container (we'll mutate its contents)
    target = pn.Column(init_target_layout)

    # Main layout: target on top, sliders below
    layout = pn.Column(
        target,
        slider_box,
        width_policy="min",  # similar intention to width="min-content"
    )
    layout.css_classes = ["m-manipulate"]

    return layout
