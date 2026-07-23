from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from desktop.platform.shared.context import ApplicationContext
from desktop.product.ui.components.expression_widget import ExpressionWidget


class MainWindow(QMainWindow):
    """
    The main UI shell for the CHITTI Companion.
    """
    def __init__(self, context: ApplicationContext) -> None:
        super().__init__()
        self.context = context
        self.setWindowTitle(f"CHITTI Companion v{self.context.version.version()}")
        self.resize(1024, 768)

        # Basic UI scaffolding
        layout = QVBoxLayout()
        label = QLabel("CHITTI AI Companion Shell")
        layout.addWidget(label)

        # Expression UI rendering
        self.expression_widget = ExpressionWidget(self.context)
        layout.addWidget(self.expression_widget, stretch=1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Subscribe to system events
        self.context.event_bus.subscribe("Theme.Changed", self._on_theme_changed)

    def _on_theme_changed(self, event: any) -> None:
        theme = event.payload.get("theme", "dark")
        self.context.logger.info(f"MainWindow responding to Theme.Changed: {theme}")
        # In the future, we load QSS stylesheets based on this value.
