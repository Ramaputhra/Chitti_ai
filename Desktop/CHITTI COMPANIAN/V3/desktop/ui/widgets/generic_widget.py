from typing import Dict, Any, Optional
from desktop.ui.widgets.sdk.widget import BaseWidget
from desktop.ui.widgets.sdk.widget_context import WidgetContext

class GenericWidgetImpl(BaseWidget):
    """
    S36D-2: Concrete Generic Widget implementation supporting all 17 generic widget types:
    Media, Reminder, Alarm, Timer, Email, Browser, Navigation, Presentation, Printer, Clipboard,
    Download, Upload, Battery, Weather, Vision, Productivity, System.
    Visualizes Runtime Session data ONLY.
    """
    def initialize(self, context: Optional[WidgetContext] = None):
        if context:
            self.context = context
        self.visible = True

    def update(self, delta_data: Dict[str, Any]):
        if self.context.session:
            self.context.session.update_data(delta_data)

    def render(self) -> str:
        sess = self.context.session
        if not sess:
            return f"<div id='{self.widget_id}' class='chitti-widget widget-{self.widget_type.lower()}'>Unbound Widget</div>"

        data_summary = ", ".join(f"{k}: {v}" for k, v in sess.data.items())
        style = self.context.theme
        return (
            f"<div id='{self.widget_id}' class='chitti-widget widget-{self.widget_type.lower()} "
            f"{'expanded' if self.expanded else 'collapsed'} {'docked' if self.docked else 'floating'}' "
            f"style='border-radius: {style.corner_radius_px}px; font-family: {style.font_family}; accent: {style.accent_color};'>\n"
            f"  <div class='widget-header'>{self.widget_type} Widget [{sess.session_id}] ({sess.owner_capability})</div>\n"
            f"  <div class='widget-body'>{data_summary}</div>\n"
            f"</div>"
        )
