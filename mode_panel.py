import time
import panel as pn
import panel.io
import itertools

import layout as lt
import mode
import util

# style sheet css
with open("assets/app_panel.css") as f:
    css = f.read()
pn.extension(raw_css=[css])


# --- Basic wrappers ----------------------------------------------------------

def wrap(s):
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


def graph(figure, height):

    # Turn off the mode bar like your original code did
    plot = pn.pane.Plotly(figure, config={"displayModeBar": False}, height=int(height))

    # Spacer to roughly reproduce the baseline centering trick
    center_baseline = pn.Spacer(width=0, height=int(height / 2))

    layout = pn.Row(center_baseline, plot)
    return layout


def manipulate(init_target_layout, sliders, eval_and_layout):

    # didn't seem effective
    #@panel.io.hold()
    def update(event=None):
        with util.Timer("slider update"):
            values = [s.value for s in pn_sliders]
            target_layout = eval_and_layout(values)
            target[:] = [target_layout]


    # build sliders
    pn_sliders = []
    cells = []    
    def add_slider(s):
        label = pn.pane.Str(s.name)
        slider = pn.widgets.FloatSlider(
            name="",
            start=s.lo,
            end=s.hi,
            step=s.step / 10,
            value=s.init,
            show_value=False,
            sizing_mode="stretch_width"
        )
        readout = pn.widgets.StaticText(value=f"{slider.value:.2f}")

        # keep target in sync with slider
        slider.param.watch(update, "value")

        # keep readout in sync with slider
        def update_readout(event):
            readout.value = f"{event.new:.2f}"
        slider.param.watch(update_readout, "value")

        # add to grid
        cells.extend([label, slider, readout])
        pn_sliders.append(slider)

    for s in sliders:
        add_slider(s)

    grid = pn.GridBox(
        *cells,
        ncols=3,
        sizing_mode="stretch_width",
        css_classes=["m-sliders"],
    )

    # target layout container (we'll mutate its contents)
    target = pn.Column(init_target_layout)

    # main layout: target on top, sliders below
    layout = pn.Column(
        target,
        grid,
        width_policy="min",
        css_classes = ["m-manipulate"]
    )

    return layout


#
# Following code is from https://github.com/holoviz/panel/issues/3193
#

from typing import TypedDict, NotRequired
from panel.custom import ReactComponent, DataEvent
import param
import panel as pn


# Note: this uses TypedDict instead of Pydantic or dataclass because Bokeh/Panel doesn't seem to
# like serializing custom classes to the frontend (and I can't figure out how to customize that).
class KeyboardShortcut(TypedDict):
    name: str
    key: str
    altKey: NotRequired[bool]
    ctrlKey: NotRequired[bool]
    metaKey: NotRequired[bool]
    shiftKey: NotRequired[bool]


class KeyboardShortcuts(ReactComponent):
    """
    Class to install global keyboard shortcuts into a Panel app.

    Pass in shortcuts as a list of KeyboardShortcut dictionaries, and then handle shortcut events in Python
    by calling `on_msg` on this component. The `name` field of the matching KeyboardShortcut will be sent as the `data`
    field in the `DataEvent`.

    Example:
    >>> shortcuts = [
        KeyboardShortcut(name="save", key="s", ctrlKey=True),
        KeyboardShortcut(name="print", key="p", ctrlKey=True),
    ]
    >>> shortcuts_component = KeyboardShortcuts(shortcuts=shortcuts)
    >>> def handle_shortcut(event: DataEvent):
            if event.data == "save":
                print("Save shortcut pressed!")
            elif event.data == "print":
                print("Print shortcut pressed!")
    >>> shortcuts_component.on_msg(handle_shortcut)
    """

    # bdl - following failed, but my change works
    #shortcuts = param.List(class_=dict)
    shortcuts = param.List()

    _esm = """
    // Hash a shortcut into a string for use in a dictionary key (booleans / null / undefined are coerced into 1 or 0)
    function hashShortcut({ key, altKey, ctrlKey, metaKey, shiftKey }) {
      return `${key}.${+!!altKey}.${+!!ctrlKey}.${+!!metaKey}.${+!!shiftKey}`;
    }

    export function render({ model }) {
      const [shortcuts] = model.useState("shortcuts");

      const keyedShortcuts = {};
      for (const shortcut of shortcuts) {
        keyedShortcuts[hashShortcut(shortcut)] = shortcut.name;
      }

      function onKeyDown(e) {
        const name = keyedShortcuts[hashShortcut(e)];
        //console.log(e, name)
        if (name) {
          e.preventDefault();
          e.stopPropagation();
          model.send_msg(name);
          return;
        }
      }

      /* bdl: I added capture:true */
      React.useEffect(() => {
        window.addEventListener('keydown', onKeyDown, {capture: true});
        return () => {
          window.removeEventListener('keydown', onKeyDown);
        };
      });

      return <></>;
    }
    """

