import unittest
import asyncio
from pathlib import Path
from desktop.intent.runtime import IntentRuntime
from desktop.speech.models import SpeechTranscribed
from desktop.intent.models import IntentRecognized, IntentClarificationRequired, IntentUnknown

class TestIntentRuntime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # We assume the config directory is created from the test suite runner, 
        # but since we're using the actual files we just wrote, we'll point to them.
        self.config_dir = Path(r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\config")
        self.events = []
        self.runtime = IntentRuntime(lambda e: self.events.append(e), self.config_dir)
        await self.runtime.initialize()
        await self.runtime.start()

    async def asyncTearDown(self):
        await self.runtime.stop()

    async def test_text_normalization_and_exact_match(self):
        # "బ్రౌజర్ ఓపెన్" normalizes to "browser open" -> OPEN_APPLICATION (confidence 1.0)
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="బ్రౌజర్ ఓపెన్", language="te"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertIsInstance(event, IntentRecognized)
        self.assertEqual(event.intent_id, "OPEN_APPLICATION")
        self.assertEqual(event.language, "te")
        self.assertGreater(event.duration_ms, 0.0)
        # Check extraction & resolution
        self.assertEqual(event.entities.get("app_name"), "chrome.exe")
        # Check metadata
        self.assertEqual(event.category, "System")

    async def test_medium_confidence_clarification(self):
        # A partial match string to trigger 0.75 - 0.94 confidence
        # "browser open please" -> len("browser open") = 12, len("browser open please") = 19
        # Score = 12/19 = 0.63 (LOW) - let's craft one that is ~0.8
        # "browser open x" -> len=14, score=12/14=0.85
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="browser open x", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertIsInstance(event, IntentClarificationRequired)
        self.assertEqual(event.intent_id, "OPEN_APPLICATION")

    async def test_low_confidence_unknown(self):
        # "this is garbage" -> LOW
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="this is garbage", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertIsInstance(event, IntentUnknown)

    async def test_entity_validation_failure(self):
        # If we ask for something not found
        # "notepad open" - Mock extractor extracts notepad.
        # But wait, we added notepad to applications.json so it will resolve to notepad.exe
        # Let's say we extract "unknown_app". Our extractor currently only hardcodes browser and notepad.
        # So "unknown open" wouldn't extract anything.
        # But validation checks if "app_name" is missing for OPEN_APPLICATION.
        # "open application" alone has no entities.
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="launch application", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        # It's an exact match but validation drops it because app_name is missing
        self.assertIsInstance(event, IntentUnknown)

if __name__ == '__main__':
    unittest.main()
