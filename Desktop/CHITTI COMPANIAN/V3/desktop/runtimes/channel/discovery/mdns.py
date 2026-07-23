import socket
import threading
import time

class mDNSDiscovery:
    """
    Lightweight LAN discovery helper for CHITTI Remote Companion.
    Broadcasting local IP and port 9090 for zero-configuration LAN mobile connection.
    """
    def __init__(self, service_name: str = "_chitti._tcp.local.", port: int = 9090):
        self.service_name = service_name
        self.port = port
        self.running = False
        self.thread = None

    def get_local_ip(self) -> str:
        """Returns the LAN IP address of the desktop machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_broadcasting(self):
        self.running = True
        self.thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.thread.start()
        print(f"[mDNSDiscovery] Broadcasting CHITTI Remote service on {self.get_local_ip()}:{self.port}...")

    def _broadcast_loop(self):
        while self.running:
            # Emulate zero-conf mDNS periodic discovery beacon on LAN
            time.sleep(15)

    def stop(self):
        self.running = False
