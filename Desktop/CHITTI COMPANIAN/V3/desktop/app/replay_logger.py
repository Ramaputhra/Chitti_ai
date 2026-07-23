import os
import json
from datetime import datetime
import dataclasses
from desktop.models.telemetry import PromptReplayRecord, ReplayMode

class ReplayLogger:
    """
    Logs PromptReplayRecords as JSONL files.
    Rule 190: Operational Data Is Not User Memory (Keep out of SQLite).
    """
    def __init__(self, log_dir: str, mode: ReplayMode = ReplayMode.FULL):
        self.log_dir = log_dir
        self.mode = mode
        
        if self.mode != ReplayMode.OFF:
            os.makedirs(self.log_dir, exist_ok=True)
            
    def _get_daily_file(self) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"{date_str}.jsonl")
        
    def log(self, record: PromptReplayRecord):
        if self.mode == ReplayMode.OFF:
            return
            
        record_dict = dataclasses.asdict(record)
        
        if self.mode == ReplayMode.METADATA_ONLY:
            record_dict.pop('request_payload', None)
            record_dict.pop('response_payload', None)
            
        file_path = self._get_daily_file()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict) + "\\n")
            
        # Also print to console for debug
        print(f"[ReplayLogger] 📝 Wrote {self.mode.value} record {record.prompt_hash} to {os.path.basename(file_path)}")
