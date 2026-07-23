import os
import shutil

class RollbackManager:
    def __init__(self):
        self.crash_count = 0
        
    def record_crash(self):
        self.crash_count += 1
        if self.crash_count >= 3:
            self.execute_rollback()
            
    def execute_rollback(self):
        print("[RollbackManager] Crash loop detected. Executing V2 artifact rollback.")
        appdata = os.environ.get("APPDATA", "")
        base_dir = os.path.join(appdata, "CHITTI_V2")
        db_path = os.path.join(base_dir, "database", "chitti_memory.db")
        bak_path = db_path + ".bak"
        
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, db_path)
            print("[RollbackManager] Database restored successfully.")
