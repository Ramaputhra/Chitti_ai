from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout
from PySide6.QtCore import Qt

class DiagnosticsWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHITTI Diagnostics")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("System Diagnostics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        form = QFormLayout()
        
        # Mock status for Sprint 134A
        # In the future, this will dynamically query the EventBus/Registry
        self.statuses = {
            "Kernel": "✅ Running",
            "Voice": "✅ Listening",
            "Planner": "✅ Ready",
            "Capabilities": "✅ Loaded",
            "Memory": "✅ Connected",
            "Internet": "✅ Connected",
            "UI": "✅ Active",
            "Expression": "✅ Active",
        }
        
        for key, status in self.statuses.items():
            lbl = QLabel(status)
            lbl.setStyleSheet("font-weight: normal; color: #333;" if "✅" in status else "color: red;")
            form.addRow(f"<b>{key}:</b>", lbl)
            
        layout.addLayout(form)
