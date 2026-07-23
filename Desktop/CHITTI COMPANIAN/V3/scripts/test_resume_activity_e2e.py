import sys
import os
import asyncio
import time
import json
import psutil
import subprocess
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop.app.context import EventBus, KernelContext, ServiceRegistry
from desktop.app.kernel import RuntimeKernel
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.planner import PlannerRuntime
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.runtimes.execution import ExecutionRuntime
from desktop.app.capability_contracts import SimpleCapabilityRegistry, CapabilityDescriptor
from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
from desktop.models.companion import ActivityMemoryModel, ActivityState
from desktop.models.cognition import ConversationIntent
from desktop.models.execution import ExecutionResult

async def run_e2e():
    print("🚀 Starting CHITTI Resume Activity E2E Physical Test")
    
    # --- 1. Load Profile ---
    profile_path = r"C:\Users\Sm!le\Desktop\CHITTI_E2E\profiles\resume_e2e.json"
    if not os.path.exists(profile_path):
        print(f"❌ Test profile not found at {profile_path}")
        return
        
    with open(profile_path, 'r') as f:
        profile = json.load(f)
        
    workspace_path = profile["workspace"]
    print(f"📦 Target Workspace: {workspace_path}")
    
    # --- 2. Bootstrap Headless Kernel ---
    registry = ServiceRegistry()
    event_bus = EventBus()
    context = KernelContext(registry, event_bus, {})
    
    memory_runtime = MemoryRuntime()
    await memory_runtime.initialize(context)
    
    planner = PlannerRuntime(strategy=DeterministicPlannerStrategy())
    await planner.initialize(context)
    
    cap_registry = SimpleCapabilityRegistry()
    cap = ResumeActivityCapability()
    cap_registry.register(CapabilityDescriptor(
        id="ResumeActivityCapability",
        version="1.0",
        permissions=[],
        execution_mode="sync",
        factory=lambda: cap
    ))
    
    executor = ExecutionRuntime(cap_registry)
    await executor.initialize(context)
    
    kernel = RuntimeKernel(context, [memory_runtime, planner, executor])
    
    # Simulate background interaction loop (we don't strictly need it running for this manual synchronous test)
    # But just in case, we have the runtimes initialized.
    
    # --- 3. Telemetry Tracking ---
    telemetry = {
        "observation_ms": 0,
        "memory_ms": 0,
        "validation_ms": 0,
        "planner_ms": 0,
        "execution_ms": 0,
        "verification_ms": 0,
        "total_e2e_ms": 0,
        "readiness_score": 0
    }
    
    t_start_e2e = time.time()
    
    try:
        # Step A: Inject Mock DB Record to simulate physical observation (To avoid polluting real DB)
        # We manually build it exactly as the Tracker would for this workspace
        from desktop.runtimes.activity.tracker import ActivityTrackerRuntime
        print("🔍 Simulating Physical Observation...")
        t_obs = time.time()
        
        # We construct a snapshot that looks like VS Code was recently opened in our test folder
        import uuid
        snapshot = ActivityMemoryModel(
            activity_id=f"act_{uuid.uuid4().hex[:8]}",
            domain="Coding",
            application="VS Code",
            workspace_path=workspace_path,
            project_name="chitti-e2e-frontend",
            launch_command=profile["launch_command"],
            readiness=profile["verification"]["url"],
            browser_url=profile["verification"]["url"],
            git_branch="main",
            last_active=datetime.utcnow(),
            resume_priority=1,
            verification={"source": "psutil"},
            state=ActivityState.ACTIVE,
            resume_confidence=1.0,
            observer_health=[],
            schema_version=1
        )
        
        telemetry["observation_ms"] = int((time.time() - t_obs) * 1000)
        
        # Save to memory (Step B)
        t_mem = time.time()
        await memory_runtime.commit_activity(snapshot)
        telemetry["memory_ms"] = int((time.time() - t_mem) * 1000)
        print(f"💾 Activity Persisted. ID: {snapshot.activity_id}")
        
        # Step C: Trigger the Planner Intent
        print("🧠 Injecting Intent -> 'Continue my project'")
        t_plan = time.time()
        
        # Create an Intent event (simulating ConversationRuntime output)
        intent = ConversationIntent(
            subtype="ResumeActivityIntent",
            query="Continue my project"
        )
        
        snapshot.activities = [snapshot] # Mocking a snapshot containing the activity
        decision = planner.strategy.formulate_decision(intent, snapshot)
        workflows = decision.plan.workflows
        telemetry["planner_ms"] = int((time.time() - t_plan) * 1000)
        
        if not workflows:
            print("❌ Planner failed to generate workflow.")
            return
            
        print(f"✅ Planner generated: {workflows[0].action}")
        
        # Step D: Physical Execution
        print("🚀 Executing Capability physically...")
        t_exec = time.time()
        
        # Directly execute the workflow via Capability instance
        req = workflows[0]
        
        # In a real environment, ExecutionRuntime unpacks parameters
        try:
            result = cap.execute(**req.parameters)
            success = True
            output = result
            error = None
        except Exception as e:
            success = False
            output = None
            error = str(e)
        
        telemetry["execution_ms"] = int((time.time() - t_exec) * 1000)
        
        if success:
            print(f"✅ Capability Succeeded: {output}")
            telemetry["readiness_score"] = 100
        else:
            print(f"❌ Capability Failed: {error}")
            telemetry["readiness_score"] = 0
            
        telemetry["total_e2e_ms"] = int((time.time() - t_start_e2e) * 1000)
        
        # --- 4. Report Generation ---
        report_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "target_workspace": workspace_path,
            "metrics": telemetry,
            "result": success
        }
        
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'reports'), exist_ok=True)
        json_path = os.path.join(os.path.dirname(__file__), '..', 'reports', 'resume_activity_e2e.json')
        md_path = os.path.join(os.path.dirname(__file__), '..', 'reports', 'resume_activity_e2e.md')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
            
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Resume Activity E2E Report\n\n")
            f.write(f"**Date:** {report_data['timestamp']}\n")
            f.write(f"**Target:** `{workspace_path}`\n")
            f.write(f"**Result:** {'✅ PASS' if success else '❌ FAIL'}\n\n")
            f.write(f"## Telemetry\n")
            f.write(f"- Observation: {telemetry['observation_ms']} ms\n")
            f.write(f"- Memory: {telemetry['memory_ms']} ms\n")
            f.write(f"- Planning: {telemetry['planner_ms']} ms\n")
            f.write(f"- Execution: {telemetry['execution_ms']} ms\n")
            f.write(f"- **Total E2E:** {telemetry['total_e2e_ms']} ms\n")
            
        print("\n📊 Generated reports in /reports/")

    except Exception as e:
        print(f"💥 E2E Test Crashed: {e}")
    finally:
        print("\n🧹 Initiating Teardown...")
        # Close python http.server running on 5173
        killed_node = 0
        killed_code = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline') or []
                name = proc.info.get('name') or ''
                
                if 'python' in name.lower() and 'http.server' in cmdline and '5173' in cmdline:
                    proc.kill()
                    killed_node += 1
                elif ('code' in name.lower() or 'Code.exe' in name) and workspace_path in cmdline:
                    proc.kill()
                    killed_code += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        print(f"🧹 Killed {killed_node} dummy dev servers.")
        print(f"🧹 Killed {killed_code} test VS Code instances.")
        await kernel.shutdown()

if __name__ == "__main__":
    asyncio.run(run_e2e())
