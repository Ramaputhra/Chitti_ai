import asyncio
from datetime import datetime
from desktop.models.memory import KnowledgeLevel, RelationType, KnowledgeRecordStatus, KnowledgeProvenance, KnowledgeRecord, KnowledgeRelationship
from desktop.models.cognition import ExtractedKnowledgeGraph, TemporaryNode, TemporaryRelationship, MergePolicy, KnowledgeSignature
from desktop.app.knowledge_validator import KnowledgeValidator

async def test_incremental_merge():
    print("--- Running Sprint 93 Incremental Update Tests ---\n")
    
    # Setup initial records
    prov1 = KnowledgeProvenance("doc1", "chunk1", "LLM", "1.0", "1.0", datetime.now(), datetime.now(), 0.9, "1.0", "model")
    
    rec_exact = KnowledgeRecord("uuid-exact", "Kernel manages lifecycle.", KnowledgeLevel.CONCEPT, prov1, KnowledgeRecordStatus.ACTIVE, 1, None)
    # For rec_sig, we assume the signature matches but text changes slightly
    rec_sig = KnowledgeRecord("uuid-sig", "Planner routes tasks.", KnowledgeLevel.CONCEPT, prov1, KnowledgeRecordStatus.ACTIVE, 1, None)
    # For rec_missing, it will not appear in the new extraction
    rec_missing = KnowledgeRecord("uuid-missing", "Ghost fact.", KnowledgeLevel.ATOMIC_FACT, prov1, KnowledgeRecordStatus.ACTIVE, 1, None)

    existing_records = [rec_exact, rec_sig, rec_missing]
    existing_relationships = [] # Keep simple for this test

    # New Extraction
    sig_exact = KnowledgeSignature("CONCEPT", ["Kernel", "lifecycle"], "chunk1")
    sig_updated = KnowledgeSignature("CONCEPT", ["Planner", "tasks"], "chunk1") # Matches rec_sig signature conceptually, but we rely on fallback text similarity for this test since old records don't store signatures yet.
    
    graph = ExtractedKnowledgeGraph(
        nodes=[
            # Exact Match
            TemporaryNode("_n1", "Kernel manages lifecycle.", KnowledgeLevel.CONCEPT, 0.9, "doc1", "chunk1", "", sig_exact),
            # Text Similarity Match (Simulates Signature match fallback)
            TemporaryNode("_n2", "The Planner intelligently routes tasks.", KnowledgeLevel.CONCEPT, 0.9, "doc1", "chunk1", "", sig_updated),
            # Brand New
            TemporaryNode("_n3", "New fact entirely.", KnowledgeLevel.ATOMIC_FACT, 0.9, "doc1", "chunk1", "", sig_exact)
        ],
        edges=[],
        metadata={"source_id": "doc1"}
    )
    
    policy = MergePolicy(exact_match=True, signature_required=False, text_similarity_threshold=0.6, allow_fallback=True)
    validator = KnowledgeValidator()
    
    records, rels, trace = validator.merge_graph(graph, existing_records, existing_relationships, policy)
    
    # Test 1: Exact Match (Unchanged)
    exact_res = next(r for r in records if r.record_id == "uuid-exact")
    assert exact_res.version == 1
    assert exact_res.status == KnowledgeRecordStatus.ACTIVE
    
    # Test 2: Text Similarity / Signature (Updated)
    sig_res = next(r for r in records if r.record_id == "uuid-sig")
    assert sig_res.content == "The Planner intelligently routes tasks."
    assert sig_res.version == 2
    assert sig_res.supersedes == "uuid-sig"
    
    # Test 3: New Node
    new_res = next(r for r in records if r.record_id not in ["uuid-exact", "uuid-sig", "uuid-missing"])
    assert new_res.version == 1
    
    # Test 4: Missing Node (Deprecated)
    missing_res = next(r for r in records if r.record_id == "uuid-missing")
    assert missing_res.status == KnowledgeRecordStatus.DEPRECATED
    
    # Verify Trace
    assert trace.unchanged_nodes == 1
    assert trace.updated_nodes == 1
    assert trace.new_nodes == 1
    assert trace.deprecated_nodes == 1
    
    print("✅ All Incremental Update Tests passed.")
    print(f"Trace: {trace}")

if __name__ == "__main__":
    asyncio.run(test_incremental_merge())
