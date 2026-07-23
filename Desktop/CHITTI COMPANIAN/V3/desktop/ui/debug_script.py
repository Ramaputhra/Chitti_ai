import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from PySide6.QtWidgets import QApplication
from desktop.ui.widget.companion_widget import CompanionWidget

app = QApplication(sys.argv)
companion = CompanionWidget()
with open("debug_output.txt", "w") as f:
    f.write(str(type(companion)) + "\n")
    f.write(str(dir(companion)) + "\n")
    if hasattr(companion, "cache"):
        f.write("Has cache!\n")
    else:
        f.write("No cache attribute!\n")
