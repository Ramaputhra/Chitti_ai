import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget

from desktop.platform.shared.context import ApplicationContext
from desktop.platform.shared.interfaces.event_bus import Event


class ExpressionWidget(QWidget):
    """
    Renders CHITTI's expressions using .mp4 clips if available,
    falling back to large emojis.
    """
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        
        # Path to EXPRESSIONS directory
        self.expressions_dir = os.path.join(os.getcwd(), "Expressions")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.stacked = QStackedWidget()
        self.layout.addWidget(self.stacked)
        
        # 1. Emoji Fallback UI
        self.emoji_label = QLabel("😐")
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setStyleSheet("font-size: 150px; background-color: #1e1e1e; color: #ffffff;")
        
        # 2. MP4 Video Player UI
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Loop video continuously
        self.media_player.mediaStatusChanged.connect(self._on_media_status_changed)
        
        self.stacked.addWidget(self.emoji_label)
        self.stacked.addWidget(self.video_widget)
        
        # Subscribe to rendering intents
        self.context.event_bus.subscribe("Expression.Render", self._on_expression_render)
        
        # Default state
        self._set_emoji("😐")

    def _on_media_status_changed(self, status):
        """Loops the video automatically."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def _on_expression_render(self, event: Event) -> None:
        pattern = event.payload.get("pattern", "Neutral")
        
        # Map emotional targets to video files
        file_map = {
            "Wide_Happy": "yeah.mp4",
            "Talking": "talking_default_loop.mp4",
            "Thumbs_Up": "thumbs_up.mp4",
            "Scroll": "turn_off_scroll.mp4",
            "Working": "working_laptop_loop.mp4",
            "Blush": "blush.mp4"
        }
        
        # Map emotional targets to emojis
        emoji_map = {
            "Wide_Happy": "😊",
            "Talking": "🗣️",
            "Thumbs_Up": "👍",
            "Scroll": "📜",
            "Working": "💻",
            "Blush": "😳",
            "Neutral": "😐"
        }
        
        filename = file_map.get(pattern)
        if filename:
            filepath = os.path.join(self.expressions_dir, filename)
            if os.path.exists(filepath):
                self._play_video(filepath)
                return
                
        # Fallback if no file is mapped or file doesn't exist
        self._set_emoji(emoji_map.get(pattern, "😐"))
        
    def _play_video(self, filepath: str) -> None:
        self.stacked.setCurrentWidget(self.video_widget)
        self.media_player.setSource(QUrl.fromLocalFile(filepath))
        self.media_player.play()
        self.context.logger.info(f"ExpressionWidget playing MP4: {os.path.basename(filepath)}")
        
    def _set_emoji(self, emoji: str) -> None:
        self.media_player.stop()
        self.stacked.setCurrentWidget(self.emoji_label)
        self.emoji_label.setText(emoji)
        self.context.logger.info(f"ExpressionWidget rendered Emoji: {emoji}")
