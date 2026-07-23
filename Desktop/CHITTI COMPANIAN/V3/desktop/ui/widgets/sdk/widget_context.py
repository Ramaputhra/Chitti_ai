from typing import Optional, Dict, Any
from desktop.ui.widgets.sdk.widget_session import WidgetSession
from desktop.ui.widgets.sdk.widget_theme import WidgetTheme

class WidgetContext:
    """
    S36D-2: Execution Context provided to BaseWidget during initialization.
    """
    def __init__(self, session: Optional[WidgetSession] = None, theme: Optional[WidgetTheme] = None):
        self.session = session
        self.theme = theme or WidgetTheme()
