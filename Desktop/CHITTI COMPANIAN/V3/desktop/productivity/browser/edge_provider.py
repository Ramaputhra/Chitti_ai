import os
import sqlite3
import tempfile
import shutil
from typing import List
from urllib.parse import urlparse
from desktop.productivity.browser.provider import BrowserProvider
from desktop.models.browser import BrowserTab

class EdgeProvider(BrowserProvider):
    
    @property
    def browser_name(self) -> str:
        return "Edge"
        
    @property
    def executable_names(self) -> List[str]:
        return ["msedge.exe"]
        
    def _get_history_path(self) -> str:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "History")
        
    def extract_recent_history(self, since_timestamp: float) -> List[BrowserTab]:
        history_path = self._get_history_path()
        if not os.path.exists(history_path):
            return []
            
        tabs = []
        temp_fd, temp_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(temp_fd)
        
        try:
            shutil.copy2(history_path, temp_path)
            
            # Edge stores timestamps as microseconds since 1601-01-01 (Chromium)
            edge_since = int((since_timestamp + 11644473600) * 1000000)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            query = """
                SELECT url, title, last_visit_time
                FROM urls
                WHERE last_visit_time > ?
                ORDER BY last_visit_time DESC
            """
            
            cursor.execute(query, (edge_since,))
            rows = cursor.fetchall()
            
            for row in rows:
                url, title, last_visit_time = row
                
                if self._should_filter(url):
                    continue
                    
                unix_visit_time = (last_visit_time / 1000000.0) - 11644473600
                domain = urlparse(url).netloc
                
                tabs.append(BrowserTab(
                    url=url,
                    title=title or "",
                    domain=domain,
                    opened_at=unix_visit_time
                ))
                
            conn.close()
        except Exception:
            pass
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        return tabs
        
    def _should_filter(self, url: str) -> bool:
        lower_url = url.lower()
        if lower_url.startswith("edge://") or lower_url.startswith("chrome-extension://"):
            return True
        if "oauth" in lower_url or "login" in lower_url:
            return True
        return False
