import os
import yaml
from typing import List, Optional
from desktop.models.component_manifest import ComponentManifest, ComponentPerformance

class ManifestLoader:
    """
    Responsible for parsing raw YAML files and converting them into
    strongly-typed ComponentManifest objects.
    """
    
    def load_from_file(self, filepath: str) -> Optional[ComponentManifest]:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return self.load_from_dict(data)

    def load_from_dict(self, data: dict) -> Optional[ComponentManifest]:
        if not data or 'component_id' not in data:
            return None
            
        perf_data = data.get('performance')
        perf = None
        if perf_data:
            perf = ComponentPerformance(
                cpu_latency_ms=perf_data.get('cpu_latency_ms'),
                gpu_latency_ms=perf_data.get('gpu_latency_ms'),
                ram_mb=perf_data.get('ram_mb'),
                vram_mb=perf_data.get('vram_mb')
            )
            
        return ComponentManifest(
            component_id=data.get('component_id'),
            component_type=data.get('component_type', 'unknown'),
            version=str(data.get('version', '1.0')),
            provider_backend=data.get('provider_backend', 'unknown'),
            runtime=data.get('runtime', 'unknown'),
            dependencies=data.get('dependencies', []),
            capabilities=data.get('capabilities', []),
            performance=perf,
            supported_devices=data.get('supported_devices', ['cpu']),
            quantizations=data.get('quantizations', []),
            license=data.get('license'),
            download_url=data.get('download_url'),
            checksum=data.get('checksum')
        )
