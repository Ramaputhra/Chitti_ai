from dataclasses import dataclass

@dataclass
class RendererCapabilities:
    """
    Capabilities advertised by the frontend during the initial connection handshake.
    """
    supports_animations: bool = True
    supports_streaming: bool = True
    supports_charts: bool = True
    supports_markdown: bool = True
    supports_video: bool = False
    protocol_version: int = 1

@dataclass
class FrontendHandshake:
    """
    The initial payload sent by a new frontend connection.
    """
    renderer_instance_id: str
    capabilities: RendererCapabilities
    client_type: str = "web" # e.g., "web", "mobile", "desktop_overlay"
