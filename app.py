import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication
from view import View
from model import Model


# Application class initializes the model and view for the GUI
class Application(QApplication):
    def __init__(self, sys_argv):
        super(Application, self).__init__(sys_argv)
        self._model = Model()
        self._view = View(self._model)


# The main function that starts the GUI application
def main():
    app = Application(sys.argv)
    app._view.show()
    sys.exit(app.exec())


# Function to convert a .ui file to a .py file using pyside6-uic
def convert_ui_file(ui_file, output_file):
    command = f"pyside6-uic {ui_file} -o {output_file}"
    subprocess.call(command, shell=True)


# Script execution starts here
if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Convert ui_design.ui to ui.py
    ui_file_path = os.path.join(script_directory, "ui_design.ui")
    convert_ui_file(ui_file_path, "ui.py")

    # Convert ui_pacer.ui to pacer_ui.py
    pacer_ui_file_path = os.path.join(script_directory, "ui_pacer.ui")
    convert_ui_file(pacer_ui_file_path, "pacer_ui.py")

    # Start the main application
    main()
