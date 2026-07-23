import json
import os
from desktop.runtimes.channel.pairing.service import PairingService
from desktop.runtimes.channel.device.registry import DeviceRegistry
from desktop.runtimes.channel.services.transfer_manager import TransferManager
from desktop.runtimes.channel.router.input import ChannelRouter
from desktop.runtimes.channel.router.output import OutputRouter
from desktop.runtimes.channel.presence.manager import PresenceManager
from desktop.runtimes.channel.transport.websocket import WebSocketTransport
from desktop.runtimes.channel.models.core import ChannelType

import http.server
import socketserver
import threading
from desktop.runtimes.channel.pairing.service import PairingService
from desktop.runtimes.channel.device.registry import DeviceRegistry
from desktop.runtimes.channel.services.transfer_manager import TransferManager
from desktop.runtimes.channel.router.input import ChannelRouter
from desktop.runtimes.channel.router.output import OutputRouter
from desktop.runtimes.channel.presence.manager import PresenceManager
from desktop.runtimes.channel.transport.websocket import WebSocketTransport
from desktop.runtimes.channel.models.core import ChannelType
from desktop.runtimes.channel.discovery.mdns import mDNSDiscovery

class ChannelRuntime:
    """
    The orchestrator of the Channel Module.
    Coordinates pairing, presence, input/output routing, LAN HTTP server, and transports.
    """
    def __init__(self):
        self.config = self._load_config()
        
        # Security & State
        self.device_registry = DeviceRegistry()
        self.pairing_service = PairingService()
        self.transfer_manager = TransferManager(self.config.get("max_transfer_size_mb", 500))
        
        # Routers
        self.output_router = OutputRouter()
        self.input_router = ChannelRouter()
        
        # Presence & Discovery
        self.presence_manager = PresenceManager(self.output_router)
        self.mdns_discovery = mDNSDiscovery(port=self.config.get("websocket_port", 9090))
        
        # Transport & HTTP Server
        self.transport = WebSocketTransport(port=self.config.get("websocket_port", 9090))
        self.http_port = self.config.get("http_port", 8080)
        self.http_thread = None
        self.desktop_locked = False
        
    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), "config", "channel_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {"websocket_port": 9090, "http_port": 8080}
        
    def start(self):
        self.transport.register_callbacks(
            on_message=self._handle_client_message,
            on_disconnect=self._handle_client_disconnect
        )
        self.transport.start_server()
        self._start_http_server()
        self.mdns_discovery.start_broadcasting()
        print(f"[ChannelRuntime] Started successfully. Web UI hosted at http://{self.mdns_discovery.get_local_ip()}:{self.http_port}")

    def _start_http_server(self):
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "remote_mobile"))
        
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=frontend_dir, **kwargs)
            def log_message(self, format, *args):
                pass # Suppress noisy server log

        def serve():
            try:
                with socketserver.TCPServer(("", self.http_port), CustomHTTPRequestHandler) as httpd:
                    httpd.serve_forever()
            except Exception as e:
                print(f"[ChannelRuntime] HTTP Server warning: {e}")

        self.http_thread = threading.Thread(target=serve, daemon=True)
        self.http_thread.start()

    def get_lock_confirmation_details(self) -> dict:
        """Returns details for desktop lock confirmation dialog."""
        return {
            "title": "Confirm Lock Desktop",
            "available_after_lock": [
                "Chat", "AI Conversation", "File Search", "File Transfer", "Upload", "Download",
                "Workflow", "Background Tasks", "Reminders", "Timers", "Notifications", "Volume Control"
            ],
            "unavailable_until_unlock": [
                "Desktop Screenshot", "Interactive Desktop Automation", "Mouse Control",
                "Keyboard Control", "Browser UI Automation", "Desktop Vision"
            ]
        }

    def set_desktop_locked(self, locked: bool):
        self.desktop_locked = locked
        print(f"[ChannelRuntime] Desktop locked status set to: {locked}")
        
    def _handle_client_message(self, device_id: str, payload: dict):
        msg_type = payload.get("type")
        
        if msg_type == "chat":
            self.input_router.route_input(ChannelType.MOBILE_CHAT, payload.get("text"))
        elif msg_type == "remote_approval":
            print(f"[ChannelRuntime] Remote Approval received: {payload.get('choice')}")
            
    def _handle_client_disconnect(self, device_id: str):
        self.presence_manager.handle_mobile_disconnected()
        
    def handle_client_connected(self, device_id: str):
        """Called by transport after successful handshake and token verification."""
        self.presence_manager.handle_mobile_connected()
        self.transport.push_message(device_id, {
            "type": "capability_advertisement",
            "supports": ["chat", "notifications", "workflow_progress", "downloads", "screenshot", "remote_approval"]
        })

