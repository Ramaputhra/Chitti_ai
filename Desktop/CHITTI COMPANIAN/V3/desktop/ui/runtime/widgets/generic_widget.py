from typing import Dict, Any
from desktop.ui.runtime.widgets.base_widget import BaseWidget

class GenericWidget(BaseWidget):
    """
    S36D: Concrete Generic Widget implementation supporting all 17 widget types:
    Media, Reminder, Alarm, Email, Browser, Navigation, Presentation, Printer, Download, Upload, Vision, Clipboard, Battery, Weather, Productivity, System, Timer.
    """
    def initialize(self):
        self.visible = True

    def update(self, delta_data: Dict[str, Any]):
        if self.session:
            self.session.data.update(delta_data)

    def render(self) -> str:
        if not self.session:
            return f"<div id='{self.widget_id}' class='widget {self.widget_type}'>Unbound Widget</div>"
        
        data_str = ", ".join(f"{k}: {v}" for k, v in self.session.data.items())
        return (
            f"<div id='{self.widget_id}' class='widget widget-{self.widget_type.lower()} "
            f"{'expanded' if self.expanded else 'collapsed'} {'docked' if self.docked else 'floating'}'>\n"
            f"  <div class='widget-header'>{self.widget_type} Widget [{self.session.session_id}]</div>\n"
            f"  <div class='widget-body'>{data_str}</div>\n"
            f"</div>"
        )
