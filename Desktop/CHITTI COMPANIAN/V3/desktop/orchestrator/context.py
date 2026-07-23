import time

class PipelineContext:
    def __init__(self, root_experience, correlation_id: str):
        self._root_experience = root_experience
        self._correlation_id = correlation_id
        self._start_time = time.time()
        self.is_cancelled = False
        self._stage_outputs = {}
        
    @property
    def root_experience(self):
        return self._root_experience
        
    @property
    def correlation_id(self):
        return self._correlation_id
        
    @property
    def start_time(self):
        return self._start_time
        
    def append_output(self, stage_name: str, output):
        if stage_name in self._stage_outputs:
            raise ValueError(f"Cannot overwrite stage output for {stage_name}")
        self._stage_outputs[stage_name] = output
        
    def get_output(self, stage_name: str):
        return self._stage_outputs.get(stage_name)
