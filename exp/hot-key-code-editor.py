import panel as pn
import param

pn.extension('ace')

class HotkeyCodeEditor(pn.reactive.ReactiveHTML):
    """Wraps Panel's CodeEditor and injects custom Ace hotkeys via JS."""

    # Expose value etc. at the outer level if you like
    value    = param.String(default="")
    language = param.String(default="python")
    theme    = param.String(default="monokai")

    # The real CodeEditor lives here
    editor = param.Parameter(precedence=-1)

    # Template just renders the child widget
    _template = """
    <div id="root">
      <div id="editor">
        ${editor}
      </div>
    </div>
    """

    _scripts = {
        # Runs after the template is rendered and children are mounted
        "render": """
          // Get the Bokeh view for the child CodeEditor
          const view = state.views.get(data.editor)[0];   // Panel < 1.4 style
          // In newer Panel versions state.views is a Map; adjust if needed:
          // const view = [...state.views.get(data.editor)][0];

          // This is the internal Ace instance used by CodeEditor
          const ace = view.editor;

          // --- Sync Python -> JS for language/theme if you care ---
          ace.session.setMode(`ace/mode/${data.language || "python"}`);
          ace.setTheme(`ace/theme/${data.theme || "monokai"}`);

          // --- Custom hotkeys -----------------------------------
          // Ctrl/Cmd-Enter: send full code to Python
          ace.commands.addCommand({
            name: "run-cell",
            bindKey: { win: "Ctrl-Enter", mac: "Command-Enter" },
            exec: function(ed) {
              // fire a Panel/Bokeh event on *this* ReactiveHTML model
              model.send_event('run-cell', { code: ed.getValue() });
            }
          });

          // Shift-Enter: send current cursor position
          ace.commands.addCommand({
            name: "shift-enter",
            bindKey: { win: "Shift-Enter", mac: "Shift-Enter" },
            exec: function(ed) {
              const pos = ed.getCursorPosition();
              model.send_event('shift-enter', { row: pos.row, column: pos.column });
            }
          });

          // You can add more ace.commands.addCommand(...) here.

          // Optional: keep outer .value in sync with the child editor
          ace.on('change', () => {
            const v = ace.getValue();
            if (v !== data.value) {
              data.value = v;   // updates param on the ReactiveHTML model
            }
          });

          // And update Ace when data.value changes from Python
          model.on('value', () => {
            if (ace.getValue() !== data.value) {
              ace.setValue(data.value || "", -1);
            }
          });
        """
    }

    def __init__(self, **params):
        # Construct the underlying CodeEditor
        editor = pn.widgets.CodeEditor(
            value=params.pop("value", ""),
            language=params.get("language", "python"),
            theme=params.get("theme", "monokai"),
            sizing_mode="stretch_width",
            height=300,
        )
        super().__init__(editor=editor, **params)

        # Mirror value both ways if you care about self.value
        editor.link(self, value='value')
        self.link(editor, value='value')

#hot = HotkeyCodeEditor(
hot = CodeEditor(
    value="Try Ctrl-Enter or Shift-Enter\nprint('Hello from Panel CodeEditor')",
    language="python",
    theme="monokai",
    height=300,
    sizing_mode="stretch_width",
)

def on_run_cell(event):
    code = event.data.get("code", "")
    print("RUN-CELL pressed, code:\n", code)

def on_shift_enter(event):
    row = event.data.get("row")
    col = event.data.get("column")
    print(f"SHIFT-ENTER at row={row}, col={col}")

hot.on_event("editor", "run-cell", on_run_cell)
hot.on_event("editor", "shift-enter", on_shift_enter)

#pn.Column("# HotkeyCodeEditor (wrapping Panel's CodeEditor)", hot).servable()
#pn.Column("foo").servable()        
hot.servable()
