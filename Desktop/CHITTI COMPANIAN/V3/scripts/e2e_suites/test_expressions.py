import asyncio
from scripts.e2e_framework import HeadlessTestHost, MockEvent
from scripts.e2e_framework import HeadlessTestHost

async def run_test():
    print("Testing Expressions E2E Pipeline (Event-Driven from STT)...")
    host = HeadlessTestHost()
    await host.start()
    
    try:
        # 1. Inject STT Event (Whisper output)
        transcript = MockEvent("USER_TRANSCRIPT_GENERATED", source="FasterWhisper", payload={"text": "Hello Chitti"})
        host.event_bus.publish(transcript)
        
        # 2. Asynchronously wait for the pipeline to complete
        narration_event = await host.wait_for_event("ExpressionRequested", timeout=5.0)
        
        # 3. Assert EventBus Emissions
        if not narration_event:
            return False, "Failed to emit ExpressionRequested after STT injection"
            
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        await host.stop()
