import os
import sys

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from desktop.app import ApplicationBootstrap, ApplicationRuntime
from desktop.services.tasks.templates.registry import TemplateRegistry
from desktop.runtimes.execution.workflow.workflow_runtime import WorkflowRuntime
from desktop.platform.shared.models.workflow import Workflow, WorkflowStep, WorkflowState

def test_template(template_id: str, parameters: dict):
    container = ApplicationBootstrap.create_composition_root()
    runtime = ApplicationRuntime(container)
    
    # Initialize all services
    runtime._initialize_services(modes=[])
    
    registry = container.resolve(TemplateRegistry)
    registry.load_all()
    
    kernel = container.resolve(WorkflowRuntime)
    
    print(f"\n--- Testing Template: {template_id} ---")
    
    try:
        # 1. Compile the template
        compiled = registry.compile_template(template_id)
        print(f"✅ Compiled successfully: {len(compiled.nodes)} nodes")
        
        # 2. Instantiate Context
        context = registry.instantiate(template_id, parameters)
        print(f"✅ Instantiated successfully.")
        
        # 3. We can simulate execution without full scheduler by just invoking CapabilityInvoker
        from desktop.runtimes.capability.invoker import CapabilityInvoker
        from desktop.platform.shared.kernel.models import ExecutionContext, CancellationToken
        invoker = container.resolve(CapabilityInvoker)
        
        exec_ctx = ExecutionContext(session_id="test", conversation_id="test", telemetry_manager=kernel.telemetry, memory_runtime=None)
        token = CancellationToken()
        
        current_node_uuid = context.cursor.current_node_uuid
        while current_node_uuid:
            node = context.compiled_nodes[current_node_uuid]
            
            # Resolve parameters using basic substitution for this test
            resolved_params = {}
            for k, v in node.parameters.items():
                if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                    param_name = v[2:-2]
                    resolved_params[k] = parameters.get(param_name, v)
                elif isinstance(v, str) and v.startswith("$"):
                    # Basic mock resolving from outputs
                    resolved_params[k] = "MOCK_RESOLVED_VALUE" 
                else:
                    resolved_params[k] = v
                    
            if getattr(node, "type", "capability") == "approval":
                print(f"Executing Node: {node.id} -> [APPROVAL REQUIRED] Message: {node.message}")
                print(f"Plan Frozen. Requesting approval for permissions: {node.permissions}")
                # Simulate user approval
                print(f"Result (Success=True): Approval Granted")
                current_node_uuid = node.next
                continue
                
            print(f"Executing Node: {node.id} -> Action: {node.action} Parameters: {resolved_params}")
            step = WorkflowStep(
                step_id=node.id,
                action=node.action,
                parameters=resolved_params,
                status=WorkflowState.RUNNING
            )
            
            result = invoker.invoke(step, exec_ctx, token)
            print(f"Result (Success={result.success}): {result.output}")
            if result.error:
                print(f"Error: {result.error}")
                break
                
            current_node_uuid = node.next
            
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_template("core.identity", {})
    test_template("core.calculator", {"expression": "2 + 2"})
    test_template("core.calculator", {"expression": "10 / 0"}) # Negative test
    test_template("utilities.time", {})
    test_template("automation.reminder", {"duration_seconds": "1", "message": "Test"})
    test_template("desktop.open_app", {"app_name": "notepad"})
    test_template("files.search", {"query": "test"})
    test_template("core.diagnostics", {})
    test_template("advanced.deep_research", {"query": "Latest breakthroughs in fusion energy"})
    test_template("desktop.write_document", {"application": "notepad", "text": "This is a test document.", "filename": "test_memo.txt"})
    test_template("system.safe_installer", {"package": "7zip", "method": "winget", "strategy": "registry"})
