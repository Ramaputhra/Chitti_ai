import unittest
from desktop.observability.logger import TelemetryEvent, AlertSeverity

class TestEE7Observability(unittest.TestCase):
    def test_telemetry_event_immutability(self):
        evt = TelemetryEvent(
            severity=AlertSeverity.INFO,
            category="TEST",
            source_service="TestService",
            payload={"test": 123}
        )
        with self.assertRaises(Exception):
            evt.severity = AlertSeverity.WARNING
            
if __name__ == '__main__':
    unittest.main()
