import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication
from view import View
from model import Model

class Application(QApplication):
    def __init__(self, sys_argv):
        super(Application, self).__init__(sys_argv)
        self._model = Model()
        self._view = View(self._model)

def main():
    app = Application(sys.argv)
    app._view.show()
    sys.exit(app.exec())

def convert_ui_file(ui_file):
    output_file = "ui.py"
    command = f"pyside6-uic {ui_file} -o {output_file}"
    subprocess.call(command, shell=True)

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    ui_file = os.path.join(script_directory, "ui_design.ui")
    convert_ui_file(ui_file)
    main()
