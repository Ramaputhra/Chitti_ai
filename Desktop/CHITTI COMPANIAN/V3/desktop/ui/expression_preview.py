import sys
import os
import traceback

# FORCE the local V3 folder to be the very first entry in sys.path
# This prevents Python from loading an older version of the 'desktop' package from site-packages.
v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from desktop.ui.widget.companion_widget import CompanionWidget

class ExpressionDeveloperTool(QWidget):
    def __init__(self, widget: CompanionWidget):
        super().__init__()
        self.widget = widget
        self.setWindowTitle("Expression Developer Tool")
        self.setFixedSize(300, 400)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Available Expressions:"))
        
        base_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\Expressions"
        if os.path.exists(base_path):
            for expr in os.listdir(base_path):
                if os.path.isdir(os.path.join(base_path, expr)):
                    btn = QPushButton(f"Play: {expr}")
                    btn.clicked.connect(lambda checked=False, e=expr: self.play_expression(e))
                    layout.addWidget(btn)
        else:
            layout.addWidget(QLabel("Expressions folder not found!"))
            
        layout.addStretch()
        
        try:
            self.widget.slide_in()
        except Exception as e:
            print("Failed to slide in:", e)

    def play_expression(self, expr_name):
        print(f"Playing expression: {expr_name}")
        try:
            self.widget.handle_expression_started(expr_name, visible=True)
        except Exception as e:
            print(f"Failed to play {expr_name}:", e)
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        companion = CompanionWidget()
        print("CompanionWidget instantiated successfully.")
        companion.show()
    except Exception as e:
        print("Failed to instantiate CompanionWidget:")
        traceback.print_exc()
        sys.exit(1)
    
    dev_tool = ExpressionDeveloperTool(companion)
    dev_tool.show()
    
    sys.exit(app.exec())
