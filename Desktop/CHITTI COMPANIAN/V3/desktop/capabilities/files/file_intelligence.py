from desktop.models.capability import CapabilityDescriptor, CapabilityParameter
from desktop.infrastructure.files.file_repository import FileRepository
from desktop.capabilities.files.hybrid_search import HybridSearchEngine
import os
import time

class FileIntelligenceCapability:
    def __init__(self, event_bus, os_automation_capability):
        self.event_bus = event_bus
        self.os_automation = os_automation_capability
        self.repo = FileRepository()
        self.descriptor = CapabilityDescriptor(
            name="file_intelligence",
            description="Locates, searches, and opens local files. Enforces Rule 7 and Rule 8.",
            parameters=[
                CapabilityParameter("action", "string", "Action intent: find, locate, open, remember_alias"),
                CapabilityParameter("query", "string", "The file to search for or open", required=False),
                CapabilityParameter("alias", "string", "The alias name to remember", required=False),
                CapabilityParameter("path", "string", "The exact file path to map to the alias", required=False)
            ]
        )
        
    def _log_activity(self, stage: str, data: dict):
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish("ActivityTimelineEvent", {
                "source": "FileIntelligence",
                "stage": stage,
                "data": data,
                "timestamp": time.time()
            })
            
    async def invoke(self, params: dict):
        action = params.get("action")
        
        if action == "remember_alias":
            alias = params.get("alias")
            path = params.get("path")
            self.repo.remember_alias(alias, path)
            return {"status": "success", "message": f"Alias '{alias}' saved."}
            
        query = params.get("query")
        if not query:
            return {"status": "error", "message": "Query required."}
            
        self._log_activity("Search Started", {"query": query, "intent": action})
        
        # 1. Check Alias First
        alias_path = self.repo.resolve_alias(query)
        if alias_path:
            if not self.repo.exists(alias_path):
                return {"status": "error", "message": f"The file for alias '{query}' is no longer available or was deleted."}
                
            self._log_activity("Selection", {"path": alias_path, "confidence": 100.0, "source": "alias"})
            self.repo.mark_opened(alias_path)
            
            if action == "open":
                await self.os_automation.invoke({"action": "open_file", "path": alias_path})
                self._log_activity("Opened", {"path": alias_path})
                return {"status": "success", "message": "Opened via alias.", "path": alias_path}
            elif action == "locate" or action == "find":
                return {"status": "success", "path": alias_path, "folder": os.path.dirname(alias_path)}
                
        # 2. Hybrid Search
        active_files = self.repo.get_all_active_files()
        self._log_activity("Candidates", {"count": len(active_files)})
        
        ranked = HybridSearchEngine.rank(query, active_files)
        
        if not ranked:
            return {"status": "error", "message": "No local files match this query."}
            
        top_file, top_score = ranked[0]
        self._log_activity("Ranking", {"top_score": top_score, "top_file": top_file["path"]})
        
        # Disambiguation logic
        # If > 98%, we just do it. If < 90%, we disambiguate.
        if top_score < 90.0:
            top_3 = [{"filename": r[0]["filename"], "path": r[0]["path"], "score": r[1]} for r in ranked[:3]]
            return {
                "status": "disambiguate", 
                "confidence": top_score,
                "message": "Found multiple options, please clarify.",
                "options": top_3
            }
            
        # We have a high confidence match (>= 90%)
        # Note: If it's between 90 and 98, we can still auto-proceed, or we could ask if there are two very close ones.
        # Following the spec: >98% never ask. <90% ask. So 90-98% acts normally (auto-proceed).
        best_path = top_file["path"]
        self.repo.mark_opened(best_path)
        self._log_activity("Selection", {"path": best_path, "confidence": top_score})
        
        if action == "open":
            await self.os_automation.invoke({"action": "open_file", "path": best_path})
            self._log_activity("Opened", {"path": best_path})
            return {"status": "success", "message": "Opened file.", "path": best_path, "confidence": top_score}
        elif action == "locate" or action == "find":
            return {"status": "success", "path": best_path, "folder": os.path.dirname(best_path), "confidence": top_score}
            
        return {"status": "error", "message": "Unknown action intent."}
