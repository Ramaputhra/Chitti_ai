import unittest
from desktop.orchestrator.response_packet import ResponsePacket

class TestEE5Runtime(unittest.TestCase):
    def test_packet_immutability(self):
        packet = ResponsePacket(text="Hi", emotion="Happy", animation="Nod")
        self.assertEqual(packet.text, "Hi")
        
if __name__ == '__main__':
    unittest.main()
