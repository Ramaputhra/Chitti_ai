import subprocess
import socket
import time
import urllib.request
from typing import List, Dict, Any, Optional
import os

try:
    import psutil
except ImportError:
    psutil = None # Handled gracefully if missing in strict environment

from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class LaunchApplicationCapability:
    """
    Physically launches a standalone application via the OS shell (e.g. VS Code, Chrome).
    Avoids shell=True.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Execution",
            supports_undo=True,
            undo_action="TerminateApplication"
        )
        
    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        app_command = context.payload.get("app_command", "")
        arguments = context.payload.get("arguments", [])
        cwd = context.payload.get("cwd")
        
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        if context.logger:
            context.logger.info(f"[LaunchApplicationCapability] Spawning: {app_command} {' '.join(arguments)}")
        try:
            import shutil
            resolved_app = shutil.which(app_command)
            use_shell = app_command.lower() in ["start", "cmd"]
            if resolved_app and resolved_app.lower().endswith(('.cmd', '.bat')):
                use_shell = True
                
            process = subprocess.Popen(
                [resolved_app or app_command] + arguments, 
                cwd=cwd, 
                shell=use_shell,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS, 
                outputs={"status": "launched", "pid": process.pid, "error": None},
                verification_data={
                    "strategy": "PROCESS",
                    "pid": process.pid,
                    "expected_state": "running"
                }
            )
        except Exception as e:
            if context.logger:
                context.logger.error(f"[LaunchApplicationCapability] Failed: {e}")
            return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"pid": None, "error": str(e)})

class ExecuteTerminalCommandCapability:
    """
    Executes a persistent terminal command (e.g. npm run dev) attached to a working directory.
    Captures PID for deep verification.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Execution", supports_undo=True)
        
    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        command = context.payload.get("command", "")
        arguments = context.payload.get("arguments", [])
        cwd = context.payload.get("cwd", "")
        
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        if context.logger:
            context.logger.info(f"[ExecuteTerminalCommandCapability] Starting Terminal: {command} {' '.join(arguments)} in {cwd}")
        try:
            # On Windows, npm is a cmd script (npm.cmd), so we must resolve it if shell=False,
            # but setting shell=True just for `npm` is safer on Windows. We will try to resolve explicitly.
            executable = command
            if os.name == 'nt' and command == 'npm':
                executable = 'npm.cmd'
                
            process = subprocess.Popen(
                [executable] + arguments,
                cwd=cwd,
                shell=False,
                stdout=subprocess.DEVNULL, # In a real app we'd stream this
                stderr=subprocess.DEVNULL
            )
            
            # Pass verification responsibility to VerificationRuntime
            if command.lower() == "taskkill" and len(arguments) >= 2:
                target_exe = arguments[1].lower()
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS, 
                    outputs={"status": "success", "pid": process.pid, "error": None},
                    verification_data={
                        "strategy": "PROCESS",
                        "target_exe": target_exe,
                        "expected_state": "terminated"
                    }
                )
                    
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS, 
                outputs={"status": "running", "pid": process.pid, "error": None},
                verification_data={
                    "strategy": "PROCESS",
                    "pid": process.pid,
                    "expected_state": "running"
                }
            )
        except Exception as e:
            if context.logger:
                context.logger.error(f"[ExecuteTerminalCommandCapability] Failed: {e}")
            return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"pid": None, "error": str(e)})

class VerifyServiceReadinessCapability:
    """
    Deep verification of service readiness: Process -> Port -> HTTP OK -> Content Signature.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Verification")
        
    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        pid = context.payload.get("pid")
        port = context.payload.get("port")
        http_url = context.payload.get("http_url")
        content_signature = context.payload.get("content_signature")
        workspace_path = context.payload.get("workspace_path")
        required_tools = context.payload.get("required_tools")
        expected_status = context.payload.get("expected_status", 200)
        
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        evidence = []
        recovery_actions = []

        # 0. Preflight checks
        if workspace_path:
            if not os.path.exists(workspace_path):
                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": "Project moved or renamed", "recovery": [{"action": "LOCATE_PROJECT", "prompt": "Project not found. Locate it?"}]})
            
            # Check dependencies if it's a node project
            if os.path.exists(os.path.join(workspace_path, "package.json")):
                if not os.path.exists(os.path.join(workspace_path, "node_modules")):
                    return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": "Missing dependencies", "recovery": [{"action": "RUN_NPM_INSTALL", "prompt": "This project hasn't been installed yet. Would you like me to run npm install?"}]})
                    
        if required_tools:
            import shutil
            for tool in required_tools:
                if not shutil.which(tool):
                    recovery_actions.append({"action": f"INSTALL_{tool.upper()}", "prompt": f"{tool} is missing. Would you like me to install it?"})
            if recovery_actions:
                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": f"Missing tools: {required_tools}", "recovery": recovery_actions})
        
        evidence = []
        
        # 1. Check Process
        if pid and psutil:
            if psutil.pid_exists(pid):
                evidence.append(f"PID {pid} is running")
            else:
                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": "Process terminated unexpectedly", "evidence": evidence})
                
        # 2. Check Port
        if port:
            port_ready = False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    port_ready = True
            if port_ready:
                evidence.append(f"Port {port} is listening")
            else:
                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": f"Port {port} not listening", "evidence": evidence})
                
        # 3. Check HTTP & Content
        if http_url:
            try:
                req = urllib.request.Request(http_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2.0) as response:
                    if response.status == expected_status:
                        evidence.append(f"HTTP {response.status} from {http_url}")
                        
                        # 4. Check Content Signature
                        if content_signature:
                            html = response.read().decode('utf-8')
                            if content_signature in html:
                                evidence.append(f"Found signature '{content_signature}'")
                            else:
                                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": "Content signature mismatch", "evidence": evidence, "recovery": []})
                    else:
                        return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": f"HTTP {response.status}", "evidence": evidence})
            except Exception as e:
                return ExecutionResult(status=ExecutionStatus.FAILED, outputs={"is_ready": False, "conflict": f"HTTP Request failed: {str(e)}", "evidence": evidence})
                
        return ExecutionResult(status=ExecutionStatus.SUCCESS, outputs={
            "is_ready": True,
            "readiness_score": 100,
            "conflict": None,
            "evidence": evidence,
            "recovery": []
        })
