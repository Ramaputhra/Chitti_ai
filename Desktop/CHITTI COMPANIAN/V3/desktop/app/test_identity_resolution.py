import asyncio
from datetime import datetime
from desktop.models.memory import (
    KnowledgeLevel, RelationType, KnowledgeRecordStatus, KnowledgeProvenance, 
    KnowledgeRecord, KnowledgeRelationship, KnowledgeIdentity, IdentityState, KnowledgeAlias
)
from desktop.models.cognition import (
    ExtractedKnowledgeGraph, TemporaryNode, TemporaryRelationship, MergePolicy, 
    KnowledgeSignature, IdentityResolutionResult
)
from desktop.app.knowledge_validator import KnowledgeValidator

async def test_identity_resolution():
    print("--- Running Sprint 93.5 Identity Resolution Tests ---\n")
    
    # 1. Existing Identity and Record from Source A
    provA = KnowledgeProvenance("docA", "chunk1", "LLM", "1.0", "1.0", datetime.now(), datetime.now(), 0.9, "1.0", "model")
    ident1 = KnowledgeIdentity("id-1", KnowledgeLevel.CONCEPT.value, IdentityState.ACTIVE)
    alias1 = KnowledgeAlias("id-1", "Runtime Kernel", "extraction", 0.9)
    recA = KnowledgeRecord("recA-1", "id-1", "Runtime Kernel manages lifecycle.", KnowledgeLevel.CONCEPT, provA, KnowledgeRecordStatus.ACTIVE, 1, None)
    
    existing_identities = [ident1]
    existing_aliases = [alias1]
    existing_records = [recA]
    existing_relationships = []

    # 2. New Extraction from Source B
    # Simulates same concept, different wording.
    sig_exact = KnowledgeSignature("CONCEPT", ["Runtime Kernel", "lifecycle"], "chunk2")
    graph = ExtractedKnowledgeGraph(
        nodes=[
            TemporaryNode("_n1", "The Runtime Kernel orchestrates application lifecycle.", KnowledgeLevel.CONCEPT, 0.9, "docB", "chunk2", "", sig_exact)
        ],
        edges=[],
        metadata={"source_id": "docB"}
    )
    
    policy = MergePolicy(allow_identity_linking=True, minimum_text_similarity=0.4)
    validator = KnowledgeValidator()
    
    idents, aliases, records, rels, trace = validator.resolve_identity(
        graph, existing_identities, existing_aliases, existing_records, existing_relationships, policy
    )
    
    # Assertions
    # Identity is reused, no new identity created
    assert trace.identity_resolution_path[0] == "cross_document_link"
    assert trace.new_records == 1
    
    # We should have the original ident1 returned
    assert len([i for i in idents if i.identity_uuid == "id-1"]) == 1
    
    # We should have two active records pointing to "id-1"
    records_for_id1 = [r for r in records if r.identity_uuid == "id-1"]
    assert len(records_for_id1) == 2
    assert records_for_id1[0].record_id == "recA-1" # The old one
    assert records_for_id1[1].record_id != "recA-1" # The new one
    assert records_for_id1[1].content == "The Runtime Kernel orchestrates application lifecycle."
    
    print("✅ Identity Linking (Cross-Document) passed.")
    print(f"Trace: {trace}")

if __name__ == "__main__":
    asyncio.run(test_identity_resolution())
