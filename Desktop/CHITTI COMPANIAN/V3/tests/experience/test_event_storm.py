import asyncio
import time
from desktop.ui.presence.presence_engine import PresenceEngine
from desktop.ui.presence.presence_state import PresenceState

class MockEventBus:
    def __init__(self):
        self.handlers = {}
        
    def subscribe(self, event_name, handler):
        self.handlers[event_name] = handler
        
    async def publish(self, event_name, data=None):
        if event_name in self.handlers:
            await self.handlers[event_name](data)

class MockRenderer:
    def __init__(self):
        self.state_history = []
        
    def __call__(self, state: PresenceState):
        self.state_history.append(state)

async def test_event_storm():
    print("Starting Event Storm Test...")
    bus = MockEventBus()
    renderer = MockRenderer()
    engine = PresenceEngine(bus, renderer)
    
    engine.start()
    
    # Let initial SLEEPING state queue
    await asyncio.sleep(0.1)
    
    events = [
        ("WakeDetected", None),
        ("LLMStarted", None),
        ("TTSStarted", None),
        ("LLMStarted", None),
        ("AutomationStarted", {"background": False}),
        ("TaskCompleted", None)
    ]
    
    start_time = time.time()
    for i in range(100):
        # Fire events rapidly
        for event, data in events:
            await bus.publish(event, data)
            # small jitter
            await asyncio.sleep(0.001)
            
    print(f"Fired 600 events in {time.time() - start_time:.2f} seconds.")
    
    # Wait for the queue to drain
    print("Waiting for queue to drain (this tests min_durations)...")
    await asyncio.sleep(10) # Enough time for a few animations to complete
    
    engine.stop()
    
    print(f"Renderer processed {len(renderer.state_history)} discrete states.")
    print("Test passed if no deadlocks occurred and program exits cleanly.")
    
if __name__ == "__main__":
    asyncio.run(test_event_storm())
