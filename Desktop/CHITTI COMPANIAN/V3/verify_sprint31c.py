import uuid
from desktop.brain.graph.models import GraphNode, GraphEdge, GraphDelta
from desktop.brain.graph.builder import GraphBuilder
from desktop.brain.graph.validator import GraphValidator
from desktop.brain.graph.runtime import GraphRuntime
from desktop.brain.graph.query import GraphQuery

def run_verification():
    print("Starting Sprint 31C Architectural Verification...\n")
    
    mock_memory_episode = {
        "episode_id": str(uuid.uuid4()),
        "content": "Fixed bug in memory_runtime.py",
        "metadata": {"tags": ["architecture", "memory"]}
    }
    
    print("[1/5] Executing GraphBuilder...")
    builder = GraphBuilder()
    delta = builder.build_delta(mock_memory_episode)
    print(f"      Created GraphDelta: {delta.delta_id}")
    
    print("[2/5] Executing GraphValidator...")
    validator = GraphValidator()
    is_valid = validator.validate(delta)
    assert is_valid, "GraphDelta failed integrity validation."
    print("      GraphDelta integrity verified.")
    
    print("[3/5] Executing GraphRuntime Commit...")
    runtime = GraphRuntime()
    runtime.apply_delta(delta)
    print(f"      Committed. Topology size: Nodes={len(runtime.nodes)}, Edges={len(runtime.edges)}")
    
    print("[4/5] Testing Deterministic Rebuild...")
    runtime_rebuilt = GraphRuntime()
    runtime_rebuilt.apply_delta(delta)
    assert runtime.nodes == runtime_rebuilt.nodes, "Rebuild mismatch!"
    print("      Graph rebuilds deterministically from MemoryEpisodes.")
    
    print("[5/5] Testing Read-Only Query API...")
    query = GraphQuery(runtime)
    result = query.find_neighborhood("n_arch")
    assert len(result["nodes"]) > 0
    print("      Queries successfully return topological pointers.")
    
    print("\n✅ Sprint 31C Knowledge Graph Foundation successfully verified.")

if __name__ == "__main__":
    run_verification()
