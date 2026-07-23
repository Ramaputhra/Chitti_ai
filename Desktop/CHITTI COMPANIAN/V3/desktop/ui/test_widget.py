import sys
import os
from PySide6.QtWidgets import QApplication

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from desktop.ui.widget.companion_widget import CompanionWidget

app = QApplication(sys.argv)
widget = CompanionWidget()
print(dir(widget))
