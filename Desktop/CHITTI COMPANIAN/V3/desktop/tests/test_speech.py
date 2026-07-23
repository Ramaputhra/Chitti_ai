import unittest
import asyncio
from desktop.speech.runtime import SpeechRuntime
from desktop.speech.models import SpeechTranscribed, SpeakerVerified
from desktop.speech.vad import SileroVAD
from desktop.speech.auth import ECAPATDNNVerifier

class TestSpeechPipeline(unittest.IsolatedAsyncioTestCase):
    async def test_runtime_initialization(self):
        events = []
        runtime = SpeechRuntime(lambda e: events.append(e))
        
        await runtime.initialize()
        # Providers should be loaded
        self.assertIn("en", runtime._providers)
        self.assertIn("te", runtime._providers)
        
    async def test_vad_mock(self):
        vad = SileroVAD()
        # Empty audio should be False
        self.assertFalse(vad.is_speech(b""))
        # Mock high energy audio
        import numpy as np
        high_energy = np.ones(100, dtype=np.int16) * 1000
        self.assertTrue(vad.is_speech(high_energy.tobytes()))
        
    async def test_auth_mock(self):
        auth = ECAPATDNNVerifier()
        # Not enrolled -> not authenticated
        result = await auth.verify(b"audio")
        self.assertFalse(result.authenticated)
        
        # Enroll
        await auth.enroll(b"audio")
        result = await auth.verify(b"audio")
        self.assertTrue(result.authenticated)
        self.assertEqual(result.speaker_id, "owner")

if __name__ == '__main__':
    unittest.main()
