import unittest
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.packages.desktop_pack.capabilities.memory_compiler import MemoryCompilerCapability
from desktop.brain.runtimes.memory_runtime import MemoryRuntime

class TestMemoryCore(unittest.TestCase):
    def setUp(self):
        import os
        if os.path.exists("test_memory.db"):
            os.remove("test_memory.db")
            
        self.compiler = MemoryCompilerCapability()
        self.runtime = MemoryRuntime(db_path="test_memory.db")
        
        # Simulated READY_FOR_MEMORY Experience from Sprint 31A
        self.experience_input = {
            "status": "READY_FOR_MEMORY",
            "experience_id": "exp_abc123",
            "fingerprint": "hash_xyz789",
            "confidence": {"overall_score": 0.9},
            "reflection": {
                "summary": "User successfully configured the testing environment and verified architecture boundaries."
            }
        }

    def test_memory_pipeline(self):
        print("\n==========================================================")
        print("[Memory Pipeline] Starting Integration Test")
        
        # 1. Compilation
        print("[MemoryCompiler] Ingesting READY_FOR_MEMORY Experience...")
        invocation = ToolInvocation(id="inv_1", tool_name="compile", arguments={"experience": self.experience_input}, confidence=1.0, source="test")
        output = self.compiler.execute(invocation)
        
        self.assertTrue(output.execution_result.success)
        payload = output.execution_result.payload
        self.assertEqual(payload["status"], "READY_FOR_PERSISTENCE")
        
        episode = payload["episode"]
        print(f"[MemoryCompiler] Compiled MemoryEpisode: {episode['identity']['episode_id']}")
        self.assertEqual(episode['identity']['source_experience_id'], "exp_abc123")
        self.assertEqual(episode['confidence']['evidence_confidence'], 0.9)
        
        # 2. Persistence
        print("[MemoryRuntime] Ingesting MemoryEpisode for persistence...")
        stored_id = self.runtime.persist(episode)
        self.assertEqual(stored_id, episode['identity']['episode_id'])
        print(f"[MemoryRuntime] Successfully persisted and indexed {stored_id}")
        
        # 3. Retrieval
        print("[MemoryRuntime] Testing retrieval...")
        results = self.runtime.retrieve("testing environment")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["state"], "INDEXED")
        print(f"[MemoryRuntime] Successfully retrieved memory: '{results[0]['summary']}'")
        print("==========================================================\n")
        import os
        if os.path.exists("test_memory.db"):
            os.remove("test_memory.db")

if __name__ == '__main__':
    unittest.main()
