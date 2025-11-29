import panel as pn
import subprocess

pn.extension()

def execute_js_code(event):
    code = js_editor.value
    try:
        # Use subprocess to run Node.js and pass the code via stdin
        process = subprocess.Popen(['node', '-e', code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate(timeout=5)
        if stderr:
            output_area.value = f"Error:\n{stderr}"
        else:
            output_area.value = f"Output:\n{stdout}"
    except Exception as e:
        output_area.value = f"Execution failed: {e}"

ed = pn.widgets.CodeEditor(
    name='JavaScript Code',
    value='console.log("Hello, world!");',
    language='javascript',
    height=200
)


run = pn.widgets.Button(name='Run JavaScript', button_type='primary')
run.on_click(execute_js_code)

help(ed)

ed.js_on_event("ready", """
  const ace = view.editor;
  ace.commands.addCommand({
    name: "shift-enter",
    bindKey: "Shift-Enter",
    exec: function(e) {
      view.model.document.get_model('%s').clicks += 1;
    }
  });
""" % run.id)


output_area = pn.widgets.TextAreaInput(name='Execution Output', height=150)

pn.Column(ed, run_button, output_area).servable()
