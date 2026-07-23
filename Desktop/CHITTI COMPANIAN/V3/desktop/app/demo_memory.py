import asyncio
from desktop.app.kernel import BootManager
from desktop.runtimes.memory import MemoryRuntime
from desktop.platform.inference.memory.dict_provider import DictMemoryProvider
from desktop.app.memory_contracts import IMemoryService
from desktop.models.events import InteractionStored, WorkingMemoryUpdated
from desktop.models.memory import SessionState

async def verify_memory_runtime():
    print("--- Memory Runtime Verification (Sprint 78) ---")
    
    boot = BootManager()
    
    # 1. Dependency Injection: Initialize MemoryRuntime with DictProvider
    provider = DictMemoryProvider()
    mem_runtime = MemoryRuntime(provider)
    
    # Register manually for demo (bypassing normal Kernel construct list)
    boot.runtimes.append(mem_runtime)
    
    success = await boot.initialize()
    assert success
    
    kernel = await boot.start()
    
    # 2. Get Service Reference
    memory: IMemoryService = boot.registry.resolve(IMemoryService)
    
    session_id = "session_1"
    wf_1 = "workflow_A"
    wf_2 = "workflow_B"
    
    print("\n[Test 1] Conversation Memory (Append-Only)")
    memory.append_interaction(session_id, "interaction_001", "user", "Hello, CHITTI.")
    memory.append_interaction(session_id, "interaction_002", "assistant", "Hello! How can I help?")
    
    history = memory.get_recent_interactions(session_id)
    assert len(history) == 2
    print(f"✅ History retrieved. Context size: {len(history)}")
    
    print("\n[Test 2] Scoped Working Memory")
    memory.set_working_memory(wf_1, "intent", "schedule_meeting")
    memory.set_working_memory(wf_2, "intent", "play_music")
    
    val_a = memory.get_working_memory(wf_1, "intent")
    val_b = memory.get_working_memory(wf_2, "intent")
    assert val_a == "schedule_meeting"
    assert val_b == "play_music"
    print(f"✅ Working memory isolated by workflow. WF_A: {val_a}, WF_B: {val_b}")
    
    print("\n[Test 3] Memory Snapshot")
    memory.close_session(session_id)
    snapshot = memory.snapshot(session_id, wf_1)
    
    assert snapshot.session_state == SessionState.CLOSED
    assert len(snapshot.recent_interactions) == 2
    assert len(snapshot.working_memory) == 1
    assert snapshot.working_memory[0].value == "schedule_meeting"
    print(f"✅ Snapshot generated successfully: State={snapshot.session_state.name}, History={len(snapshot.recent_interactions)}, Scratchpad={len(snapshot.working_memory)}")
    
    print("\n[Test 4] Shutdown Flush")
    await kernel.shutdown()
    print("✅ System Shutdown (Provider Flushed)")

if __name__ == "__main__":
    asyncio.run(verify_memory_runtime())
