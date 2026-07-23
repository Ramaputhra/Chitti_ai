from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QTimer, Property, Signal
from PySide6.QtGui import QGuiApplication, QPainterPath, QRegion, QPainter
from desktop.ui.widget.expression_controller import ExpressionController
import os
from desktop.ui.widget.animation_cache import AnimationCache
from desktop.ui.widget.expression_player import ExpressionPlayer

class RoundedLabel(QLabel):
    def paintEvent(self, event):
        if not self.pixmap() or self.pixmap().isNull():
            super().paintEvent(event)
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        pm = self.pixmap()
        # Center the pixmap exactly like QLabel with Qt.AlignCenter
        x = (self.width() - pm.width()) // 4
        y = (self.height() - pm.height()) // 4
        pm_rect = QRect(x, y, pm.width(), pm.height())
        
        path = QPainterPath()
        # Apply the 4px curve precisely to the edges of the image
        path.addRoundedRect(pm_rect, 14, 14)
        
        painter.setClipPath(path)
        painter.drawPixmap(pm_rect, pm)

class CompanionWidget(QWidget):
    """
    The PySide6 Renderer. 
    It knows nothing about logic, it only maps renderer profiles to graphical outputs.
    """
    template_requested_signal = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.template_requested_signal.connect(self.render_template)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setFixedSize(300, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = RoundedLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TranslucentBackground)
        layout.addWidget(self.label)
        
        # Load Cache and setup Player
        base_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\Expressions"
        self.cache = AnimationCache(base_path)
        self.cache.load_all(target_size=(300, 300))
        
        self.player = ExpressionPlayer(self.cache)
        self.player.frame_updated.connect(self.label.setPixmap)
        
        self.player.play_animation("Idle")
        
        # Screen positioning - Stick to right screen edge
        screen_geo = QGuiApplication.primaryScreen().geometry()
        self._screen_x = screen_geo.width() - self.width() # 0px margin from right edge
        self._visible_y = 50
        self._hidden_y = -self.height() - 20
        
        self.move(self._screen_x, self._hidden_y)
        self._is_visible = False

    def handle_expression_started(self, animation_name: str, visible: bool = True):
        """Called by ExpressionController when a visual expression starts."""
        
        # Visibility logic
        if not visible:
            self.slide_out()
        else:
            self.slide_in()
            
        self.player.play_animation(animation_name)

    def handle_state_change(self, state: str):
        """Maps presence controller states to expressions."""
        # Simple mapping for the demo
        if state == "listening":
            self.handle_expression_started("Listening", visible=True)
        elif state == "thinking":
            self.handle_expression_started("Thinking", visible=True)
        elif state == "speaking":
            self.handle_expression_started("Speaking", visible=True)
        elif state == "idle":
            self.handle_expression_started("Idle", visible=True)
        else:
            self.handle_expression_started("Idle", visible=False)

    def trigger_event_animation(self, event_name: str):
        """Called to trigger a one-shot event animation, e.g. 'Yeah'"""
        self.player.play_animation(event_name, is_event=True)

    def slide_in(self):
        if self._is_visible:
            return
        self._is_visible = True
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self._screen_x, self._hidden_y, 300, 300))
        self.anim.setEndValue(QRect(self._screen_x, self._visible_y, 300, 300))
        self.anim.start()

    def slide_out(self):
        if not self._is_visible:
            return
        self._is_visible = False
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self._screen_x, self._visible_y, self.width(), self.height()))
        self.anim.setEndValue(QRect(self._screen_x, self._hidden_y, self.width(), self.height()))
        self.anim.start()

    def render_template(self, template_name: str, template_data: dict):
        """Renders a beautiful card based on the template name."""
        if template_name == "DistanceCard":
            origin = template_data.get("origin", "Here")
            dest = template_data.get("destination", "Unknown")
            dist = template_data.get("distance_km", "?")
            dur = template_data.get("duration_min", "?")
            
            # Beautiful HTML-like styling for QLabel
            html = f"""
            <div style='background-color: rgba(20,20,30,220); padding: 10px; border-radius: 12px; font-family: sans-serif; color: white;'>
                <h3 style='margin: 0; color: #4DA8DA;'>🗺️ Route to {dest}</h3>
                <p style='margin: 5px 0; font-size: 14px; color: #CCC;'>From: {origin}</p>
                <div style='display: flex; justify-content: space-between; margin-top: 10px;'>
                    <span style='font-size: 20px; font-weight: bold;'>{dist} km</span>
                    <span style='font-size: 18px; color: #AEE2FF;'>🚗 {dur} min</span>
                </div>
            </div>
            """
            
            # Update UI
            self.setFixedSize(320, 140)
            self.label.setText(html)
            self.label.setStyleSheet("") # Clear base style to let HTML render
            self.slide_in()
