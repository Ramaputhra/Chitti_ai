from typing import Optional, Dict, Any, List
from desktop.capabilities.base import Capability, CapabilityResult
from desktop.app.context import KernelContext
from desktop.runtimes.session_runtime import SessionRuntime

class SessionManagerCapability(Capability):
    """
    Exposes intents for session management to the Planner.
    - alias_session
    - generate_restore_plan
    - query_session
    """
    
    def __init__(self, context: KernelContext, session_runtime: SessionRuntime):
        self.context = context
        self.session_runtime = session_runtime
        
    def get_name(self) -> str:
        return "SessionManager"
        
    def get_description(self) -> str:
        return "Manages work sessions. Can alias the current session, generate automation plans to restore previous sessions, or query recent session history."

    async def execute(self, action: str, parameters: dict) -> CapabilityResult:
        if action == "alias_session":
            return await self._alias_session(parameters)
        elif action == "generate_restore_plan":
            return await self._generate_restore_plan(parameters)
        elif action == "query_session":
            return await self._query_session(parameters)
        return CapabilityResult(success=False, error=f"Unknown action {action}")

    async def _alias_session(self, parameters: dict) -> CapabilityResult:
        alias_name = parameters.get("name")
        if not alias_name:
            return CapabilityResult(success=False, error="Alias name is required.")
            
        if self.session_runtime.active_session:
            self.session_runtime.active_session.aliases.add(alias_name)
            return CapabilityResult(
                success=True, 
                data={"message": f"Successfully tagged the current session as '{alias_name}'."}
            )
        else:
            return CapabilityResult(success=False, error="No active session to alias.")
            
    async def _generate_restore_plan(self, parameters: dict) -> CapabilityResult:
        # MVP: Simulating retrieval from MemoryRuntime (which we know stores WORK_SESSION episodes)
        session_id_or_alias = parameters.get("identifier")
        if not session_id_or_alias:
            return CapabilityResult(success=False, error="Session identifier is required.")
            
        # In a real implementation, this would query MemoryRuntime for Episode type=WORK_SESSION matching the alias
        # For MVP, we mock the return to demonstrate the flow
        mock_plan = [
            {"step": 1, "action": "Launch VS Code", "target": "D:\\Projects\\CHITTI"},
            {"step": 2, "action": "Launch Terminal", "target": "D:\\Projects\\CHITTI"},
            {"step": 3, "action": "Launch Browser", "target": "GitHub - Project"}
        ]
        
        return CapabilityResult(
            success=True,
            data={
                "automation_plan": mock_plan,
                "message": f"Generated restore plan for {session_id_or_alias}."
            }
        )

    async def _query_session(self, parameters: dict) -> CapabilityResult:
        timeframe = parameters.get("timeframe", "yesterday")
        # MVP: Mock memory query
        return CapabilityResult(
            success=True,
            data={
                "summary": f"Yesterday you worked on the CHITTI desktop project for 3 hours and 18 minutes. You mainly used VS Code, Windows Terminal, and Chrome."
            }
        )
