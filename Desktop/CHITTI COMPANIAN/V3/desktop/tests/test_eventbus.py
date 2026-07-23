import unittest
import asyncio
from desktop.core.eventbus import EventBus
from desktop.models.events import SystemEvent
from desktop.intent.models import IntentRecognized
from desktop.workflow.models import WorkflowCreated
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SpeakerVerified(SystemEvent):
    event_type: str = "SpeakerVerified"
    speaker_id: str = "unknown"

class TestEventBusConcurrency(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.event_bus = EventBus()
        self.received_events = []

        async def callback(event: SystemEvent):
            self.received_events.append(event)
            await asyncio.sleep(0.001)

        self.event_bus.subscribe(IntentRecognized, callback)
        self.event_bus.subscribe(SpeakerVerified, callback)

    async def test_high_volume_concurrency(self):
        # 1000 simultaneous events
        tasks = []
        for i in range(1000):
            event = IntentRecognized(intent_id=f"TEST_{i}")
            tasks.append(self.event_bus.publish(event, "IntentRuntime"))

        await asyncio.gather(*tasks)
        
        self.assertEqual(len(self.received_events), 1000)

    async def test_event_ownership_rejection(self):
        # Unauthorized publisher (WorkflowRuntime shouldn't publish SpeakerVerified)
        event = SpeakerVerified(speaker_id="owner")
        
        # Publish authorized
        await self.event_bus.publish(event, "SpeechRuntime")
        self.assertEqual(len(self.received_events), 1)

        # Publish unauthorized
        await self.event_bus.publish(event, "WorkflowRuntime")
        # Should be dropped by EventSourceValidator
        self.assertEqual(len(self.received_events), 1)

if __name__ == '__main__':
    unittest.main()
