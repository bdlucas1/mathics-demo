import panel as pn
import param

from panel.custom import JSComponent  # Panel >= 1.8
pn.extension()

class AceEditorJS(JSComponent):
    """Simple Ace editor with custom hotkeys via JSComponent."""
    
    value    = param.String(default="", doc="Editor text")
    language = param.String(default="python")
    theme    = param.String(default="monokai")

    _esm = r"""
    // We load Ace from a CDN as an ES module. Adjust version if you like.
    import ace from "https://esm.sh/ace-builds@1.32.6/src-noconflict/ace.js";

    // You can pre-load specific modes/themes here or lazy-load them.
    import "https://esm.sh/ace-builds@1.32.6/src-noconflict/mode-python.js";
    import "https://esm.sh/ace-builds@1.32.6/src-noconflict/theme-monokai.js";

    export function render({ model, el }) {
      // Container div for Ace
      const div = document.createElement('div');
      div.style.width = '100%';
      div.style.height = '100%';
      el.appendChild(div);

      // Create Ace editor
      const editor = ace.edit(div);
      editor.session.setMode(`ace/mode/${model.language || "python"}`);
      editor.setTheme(`ace/theme/${model.theme || "monokai"}`);
      editor.setValue(model.value || "", -1);  // -1 => keep cursor position

      // --- Sync JS -> Python: when text changes, update model.value ----
      editor.on('change', () => {
        const newValue = editor.getValue();
        if (newValue !== model.value) {
          model.value = newValue;
        }
      });

      // --- Sync Python -> JS: when model.value changes, update Ace ----
      model.on('value', () => {
        if (editor.getValue() !== model.value) {
          const pos = editor.getCursorPosition();
          editor.setValue(model.value || "", -1);
          editor.moveCursorToPosition(pos);
        }
      });

      // --- Custom hotkeys ---------------------------------------------
      // Ctrl/Cmd-Enter: send full code back to Python as 'run-cell'
      editor.commands.addCommand({
        name: "run-cell",
        bindKey: { win: "Ctrl-Enter", mac: "Command-Enter" },
        exec: function(ed) {
          model.send_event('run-cell', { code: ed.getValue() });
        }
      });

      // Shift-Enter: send current line index as 'shift-enter'
      editor.commands.addCommand({
        name: "shift-enter",
        bindKey: { win: "Shift-Enter", mac: "Shift-Enter" },
        exec: function(ed) {
          const pos = ed.getCursorPosition();
          model.send_event('shift-enter', { row: pos.row, column: pos.column });
        }
      });

      // You can add more commands here:
      // editor.commands.addCommand({ name, bindKey, exec });

      return div;
    }
    """


editor = AceEditorJS(
    value="# Try Ctrl-Enter or Shift-Enter\nprint('Hello from Ace')",
    height=300,
    sizing_mode="stretch_width",
)

# Handle "run-cell" hotkey
def handle_run_cell(event):
    code = event.data.get("code", "")
    print("RUN-CELL hotkey pressed with code:\n", code)

# Handle "shift-enter" hotkey
def handle_shift_enter(event):
    row = event.data.get("row")
    col = event.data.get("column")
    print(f"SHIFT-ENTER at row={row}, col={col}")

editor.on_event("run-cell", handle_run_cell)
editor.on_event("shift-enter", handle_shift_enter)

pn.Column("# AceEditorJS demo", editor).servable()
    
