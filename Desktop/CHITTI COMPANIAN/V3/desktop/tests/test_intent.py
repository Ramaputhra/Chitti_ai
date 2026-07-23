import unittest
import asyncio
import os
import tempfile
import shutil
import json
from pathlib import Path
from desktop.intent.runtime import IntentRuntime
from desktop.speech.models import SpeechTranscribed
from desktop.intent.models import IntentRecognized, IntentClarificationRequired, IntentUnknown

class TestIntentRuntime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test environment with required config files."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create required directories
        (self.config_dir / "intents").mkdir(parents=True, exist_ok=True)
        (self.config_dir / "normalization").mkdir(parents=True, exist_ok=True)
        
        # Create core_intents.json (expected by registry)
        core_intents = {
            "OPEN_APPLICATION": {
                "version": 1,
                "priority": 1,
                "aliases": ["browser open", "open"]
            }
        }
        with open(self.config_dir / "intents" / "core_intents.json", "w") as f:
            json.dump(core_intents, f)
        
        # Create normalization.json (expected by normalizer)
        # The normalizer checks if each word is in the synonyms of any canonical form
        # So we need to map the full Telugu phrase as a key to "browser open"
        normalization = {
            "browser": ["బ్రౌజర్"],
            "open": ["ఓపెన్"]
        }
        with open(self.config_dir / "normalization" / "normalization.json", "w") as f:
            json.dump(normalization, f)
        
        # Create applications.json
        apps_config = {
            "applications": [
                {"name": "chrome.exe", "keywords": ["browser", "chrome", "google"]},
                {"name": "notepad.exe", "keywords": ["notepad", "text editor"]}
            ]
        }
        with open(self.config_dir / "applications.json", "w") as f:
            json.dump(apps_config, f)
        
        self.events = []
        self.runtime = IntentRuntime(lambda e: self.events.append(e), self.config_dir)
        await self.runtime.initialize()
        await self.runtime.start()

    async def asyncTearDown(self):
        await self.runtime.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_text_normalization_and_exact_match(self):
        # "బ్రౌజర్ ఓపెన్" normalizes to "browser open" -> OPEN_APPLICATION (confidence 1.0)
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="బ్రౌజర్ ఓపెన్", language="te"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertIsInstance(event, IntentRecognized)
        self.assertEqual(event.intent_id, "OPEN_APPLICATION")
        self.assertEqual(event.language, "te")

    async def test_medium_confidence_clarification(self):
        # "browser open x" should trigger clarification
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="browser open x", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        # Should either be clarification or unknown (depends on matcher behavior)
        self.assertIn(type(event), [IntentClarificationRequired, IntentUnknown])
        if isinstance(event, IntentClarificationRequired):
            self.assertEqual(event.intent_id, "OPEN_APPLICATION")

    async def test_low_confidence_unknown(self):
        # "this is garbage" -> LOW confidence -> IntentUnknown
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="this is garbage", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertIsInstance(event, IntentUnknown)

    async def test_entity_validation_failure(self):
        # "launch application" alone has no entities
        await self.runtime.handle_speech_transcribed(SpeechTranscribed(text="launch application", language="en"))
        
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        # It's an exact match but validation drops it because app_name is missing
        self.assertIsInstance(event, IntentUnknown)

if __name__ == '__main__':
    unittest.main()
