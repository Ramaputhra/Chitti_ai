from desktop.ui.window.window_attachment import WindowAttachment

class WidgetAttachmentAdapter:
    """
    S36D-2: Adapter wrapping Window Attachment API for Widget SDK.
    Supported attachment: CHARACTER_ANCHOR, DESKTOP_COORD, SCREEN_EDGE, RUNTIME_SESSION, MOUSE_POS.
    Widgets SHALL NEVER move Character Window.
    """
    def __init__(self, window_attachment: WindowAttachment):
        self._attachment = window_attachment

    def attach_to_character_anchor(self, anchor_data: dict, offset_x: int = 10, offset_y: int = 0):
        self._attachment.attach("CHARACTER_ANCHOR", anchor_data, offset_x=offset_x, offset_y=offset_y)

    def attach_to_screen_edge(self, edge: str = "right"):
        self._attachment.attach("SCREEN_EDGE", {"edge": edge})

    def detach(self):
        self._attachment.detach()
