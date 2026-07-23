import uuid
import difflib
from typing import Tuple, List, Dict, Optional
from datetime import datetime
from desktop.models.cognition import (
    ExtractedKnowledgeGraph, MergePolicy, KnowledgeMergeTrace, 
    TemporaryNode, TemporaryRelationship, KnowledgeSignature,
    IdentityResolutionResult, IdentityEvidence
)
from desktop.models.memory import (
    KnowledgeRecord, KnowledgeRelationship, KnowledgeProvenance, 
    KnowledgeRecordStatus, KnowledgeIdentity, IdentityState, KnowledgeAlias
)

class KnowledgeValidator:
    """
    Deterministically validates and resolves an LLM-proposed ExtractedKnowledgeGraph.
    - Uses Identity Resolution to map evidence to KnowledgeIdentities.
    - Creates or updates KnowledgeRecords representing the supporting evidence.
    """
    
    def __init__(self, node_confidence_threshold: float = 0.7, edge_confidence_threshold: float = 0.5):
        self.node_confidence_threshold = node_confidence_threshold
        self.edge_confidence_threshold = edge_confidence_threshold
        
    def _signatures_match(self, sig1: KnowledgeSignature, sig2: KnowledgeSignature) -> bool:
        if not sig1 or not sig2:
            return False
        return (sig1.knowledge_type == sig2.knowledge_type and
                sig1.source_chunk == sig2.source_chunk and
                sorted(sig1.normalized_entities) == sorted(sig2.normalized_entities) and
                sig1.relation_subject == sig2.relation_subject and
                sig1.relation_object == sig2.relation_object)
                
    def _text_similarity(self, text1: str, text2: str) -> float:
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def resolve_identity(self, 
                    graph: ExtractedKnowledgeGraph, 
                    existing_identities: List[KnowledgeIdentity] = None,
                    existing_aliases: List[KnowledgeAlias] = None,
                    existing_records: List[KnowledgeRecord] = None, 
                    existing_relationships: List[KnowledgeRelationship] = None,
                    policy: MergePolicy = None) -> Tuple[List[KnowledgeIdentity], List[KnowledgeAlias], List[KnowledgeRecord], List[KnowledgeRelationship], KnowledgeMergeTrace]:
        
        if existing_identities is None: existing_identities = []
        if existing_aliases is None: existing_aliases = []
        if existing_records is None: existing_records = []
        if existing_relationships is None: existing_relationships = []
        if policy is None: policy = MergePolicy()
            
        trace = KnowledgeMergeTrace()
        start_time = datetime.now()
        
        resolved_identities = []
        resolved_aliases = []
        resolved_records = []
        resolved_relationships = []
        
        id_map: Dict[str, str] = {} # temp_id -> identity_uuid
        
        matched_record_ids = set()
        
        # We need to map existing identities to their records for quick lookup
        identity_to_records = {}
        for r in existing_records:
            if r.status == KnowledgeRecordStatus.ACTIVE:
                identity_to_records.setdefault(r.identity_uuid, []).append(r)
        
        # 1. Identity Resolution for Nodes
        for temp_node in graph.nodes:
            if temp_node.confidence < self.node_confidence_threshold:
                continue
                
            if not temp_node.source_id or not temp_node.chunk_id:
                continue
            
            best_identity_match: Optional[str] = None
            resolution_result = IdentityResolutionResult.NEW_IDENTITY
            
            # Gather Evidence
            for identity in existing_identities:
                if identity.lifecycle_state != IdentityState.ACTIVE:
                    continue
                    
                records_for_id = identity_to_records.get(identity.identity_uuid, [])
                
                # Check for same source chunk records
                same_chunk_record = next((r for r in records_for_id if r.provenance.chunk_id == temp_node.chunk_id and r.provenance.source_id == temp_node.source_id), None)
                
                if same_chunk_record:
                    # Stage 1: Exact Text Match in same chunk
                    if same_chunk_record.content == temp_node.statement:
                        best_identity_match = identity.identity_uuid
                        resolution_result = IdentityResolutionResult.MATCH_EXISTING
                        matched_record_ids.add(same_chunk_record.record_id)
                        trace.identity_resolution_path.append("exact_match")
                        break
                        
                    # Stage 2: Text similarity
                    sim = self._text_similarity(same_chunk_record.content, temp_node.statement)
                    if sim >= policy.minimum_text_similarity:
                        best_identity_match = identity.identity_uuid
                        resolution_result = IdentityResolutionResult.MATCH_EXISTING
                        matched_record_ids.add(same_chunk_record.record_id)
                        trace.identity_resolution_path.append("high_text_similarity")
                        break
                        
                # Stage 3: Cross-document identity linking
                if policy.allow_identity_linking and not best_identity_match:
                    for r in records_for_id:
                        # Assuming signature exists conceptually. We use text similarity as fallback proxy for signature in this basic implementation.
                        sim = self._text_similarity(r.content, temp_node.statement)
                        if sim >= policy.minimum_text_similarity:
                            best_identity_match = identity.identity_uuid
                            resolution_result = IdentityResolutionResult.NEW_EVIDENCE
                            trace.identity_resolution_path.append("cross_document_link")
                            break
                            
                if best_identity_match:
                    break
            
            provenance = KnowledgeProvenance(
                source_id=temp_node.source_id,
                chunk_id=temp_node.chunk_id,
                extractor=graph.metadata.get("extractor", "unknown"),
                extractor_version=graph.metadata.get("extractor_version", "1.0"),
                embedding_version=graph.metadata.get("embedding_version", "1.0"),
                ingestion_timestamp=datetime.now(),
                validation_timestamp=datetime.now(),
                confidence=temp_node.confidence,
                prompt_version=graph.metadata.get("prompt_version", "1.0"),
                model=graph.metadata.get("model", "unknown")
            )
            
            if best_identity_match:
                id_map[temp_node.temp_id] = best_identity_match
                
                # Check if we are updating an existing record or creating a new piece of evidence
                if resolution_result == IdentityResolutionResult.MATCH_EXISTING:
                    trace.updated_records += 1
                    old_rec = next(r for r in existing_records if r.record_id in matched_record_ids and r.identity_uuid == best_identity_match)
                    
                    new_rec = KnowledgeRecord(
                        record_id=old_rec.record_id,
                        identity_uuid=best_identity_match,
                        content=temp_node.statement,
                        level=temp_node.level,
                        provenance=provenance,
                        status=KnowledgeRecordStatus.ACTIVE,
                        version=old_rec.version + 1 if old_rec.content != temp_node.statement else old_rec.version,
                        supersedes=old_rec.record_id if old_rec.content != temp_node.statement else old_rec.supersedes,
                        embedding=None,
                        embedding_metadata=None
                    )
                    resolved_records.append(new_rec)
                    if old_rec.content == temp_node.statement:
                        trace.unchanged_records += 1
                        trace.updated_records -= 1
                else:
                    # NEW_EVIDENCE for existing identity
                    trace.new_records += 1
                    new_rec = KnowledgeRecord(
                        record_id=str(uuid.uuid4()),
                        identity_uuid=best_identity_match,
                        content=temp_node.statement,
                        level=temp_node.level,
                        provenance=provenance,
                        status=KnowledgeRecordStatus.ACTIVE,
                        version=1,
                        supersedes=None
                    )
                    resolved_records.append(new_rec)
                    
            else:
                # NEW_IDENTITY
                trace.new_records += 1
                identity_uuid = str(uuid.uuid4())
                id_map[temp_node.temp_id] = identity_uuid
                trace.identity_resolution_path.append("new_identity")
                
                new_identity = KnowledgeIdentity(
                    identity_uuid=identity_uuid,
                    knowledge_type=temp_node.level.value,
                    lifecycle_state=IdentityState.ACTIVE
                )
                resolved_identities.append(new_identity)
                
                # Assume the statement itself or entities act as the initial alias
                alias_str = temp_node.statement[:50] + "..." if len(temp_node.statement) > 50 else temp_node.statement
                new_alias = KnowledgeAlias(
                    identity_uuid=identity_uuid,
                    alias=alias_str,
                    source="extraction",
                    confidence=temp_node.confidence
                )
                resolved_aliases.append(new_alias)
                
                new_rec = KnowledgeRecord(
                    record_id=str(uuid.uuid4()),
                    identity_uuid=identity_uuid,
                    content=temp_node.statement,
                    level=temp_node.level,
                    provenance=provenance,
                    status=KnowledgeRecordStatus.ACTIVE,
                    version=1,
                    supersedes=None
                )
                resolved_records.append(new_rec)
                
        # Deprecate unmatched records from the same source
        source_id = graph.metadata.get("source_id")
        if source_id:
            for old_rec in existing_records:
                if old_rec.status == KnowledgeRecordStatus.ACTIVE and old_rec.provenance.source_id == source_id and old_rec.record_id not in matched_record_ids:
                    trace.deprecated_records += 1
                    dep_rec = KnowledgeRecord(
                        record_id=old_rec.record_id,
                        identity_uuid=old_rec.identity_uuid,
                        content=old_rec.content,
                        level=old_rec.level,
                        provenance=old_rec.provenance,
                        status=KnowledgeRecordStatus.DEPRECATED,
                        version=old_rec.version,
                        supersedes=old_rec.supersedes,
                        embedding=old_rec.embedding,
                        embedding_metadata=old_rec.embedding_metadata
                    )
                    resolved_records.append(dep_rec)
                elif old_rec.status != KnowledgeRecordStatus.ACTIVE or old_rec.provenance.source_id != source_id:
                    resolved_records.append(old_rec)
        else:
            resolved_records.extend(existing_records)

        # 2. Relationship Merge
        matched_rel_ids = set()
        for temp_edge in graph.edges:
            if temp_edge.confidence < self.edge_confidence_threshold:
                continue
                
            if temp_edge.source_temp_id not in id_map or temp_edge.target_temp_id not in id_map:
                continue
                
            source_uuid = id_map[temp_edge.source_temp_id]
            target_uuid = id_map[temp_edge.target_temp_id]
            
            if source_uuid == target_uuid:
                continue
            
            matched_rel = None
            for old_rel in existing_relationships:
                if old_rel.status == KnowledgeRecordStatus.ACTIVE and old_rel.relationship_id not in matched_rel_ids:
                    if (old_rel.source_identity_uuid == source_uuid and 
                        old_rel.target_identity_uuid == target_uuid and 
                        old_rel.relation_type == temp_edge.relation_type):
                        matched_rel = old_rel
                        break
                        
            rel_provenance = KnowledgeProvenance(
                source_id=graph.metadata.get("source_id", "unknown"),
                chunk_id="relationship",
                extractor=graph.metadata.get("extractor", "unknown"),
                extractor_version=graph.metadata.get("extractor_version", "1.0"),
                embedding_version=graph.metadata.get("embedding_version", "1.0"),
                ingestion_timestamp=datetime.now(),
                validation_timestamp=datetime.now(),
                confidence=temp_edge.confidence,
                prompt_version=graph.metadata.get("prompt_version", "1.0"),
                model=graph.metadata.get("model", "unknown")
            )
            
            if matched_rel:
                trace.merged_relationships += 1
                matched_rel_ids.add(matched_rel.relationship_id)
                new_rel = KnowledgeRelationship(
                    relationship_id=matched_rel.relationship_id,
                    source_identity_uuid=source_uuid,
                    target_identity_uuid=target_uuid,
                    relation_type=temp_edge.relation_type,
                    provenance=rel_provenance,
                    status=KnowledgeRecordStatus.ACTIVE,
                    version=matched_rel.version,
                    supersedes=matched_rel.supersedes
                )
                resolved_relationships.append(new_rel)
            else:
                trace.new_relationships += 1
                new_rel = KnowledgeRelationship(
                    relationship_id=str(uuid.uuid4()),
                    source_identity_uuid=source_uuid,
                    target_identity_uuid=target_uuid,
                    relation_type=temp_edge.relation_type,
                    provenance=rel_provenance,
                    status=KnowledgeRecordStatus.ACTIVE,
                    version=1,
                    supersedes=None
                )
                resolved_relationships.append(new_rel)
                
        # Deprecate relationships if allowed by policy
        if source_id:
            for old_rel in existing_relationships:
                if old_rel.status == KnowledgeRecordStatus.ACTIVE and old_rel.provenance.source_id == source_id and old_rel.relationship_id not in matched_rel_ids:
                    trace.inactive_relationships += 1
                    dep_rel = KnowledgeRelationship(
                        relationship_id=old_rel.relationship_id,
                        source_identity_uuid=old_rel.source_identity_uuid,
                        target_identity_uuid=old_rel.target_identity_uuid,
                        relation_type=old_rel.relation_type,
                        provenance=old_rel.provenance,
                        status=KnowledgeRecordStatus.DEPRECATED,
                        version=old_rel.version,
                        supersedes=old_rel.supersedes
                    )
                    resolved_relationships.append(dep_rel)
                elif old_rel.status != KnowledgeRecordStatus.ACTIVE or old_rel.provenance.source_id != source_id:
                    resolved_relationships.append(old_rel)
        else:
            resolved_relationships.extend(existing_relationships)
                
        # Include any existing identities/aliases that weren't modified directly here
        resolved_identities.extend(existing_identities)
        resolved_aliases.extend(existing_aliases)
                
        trace.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return resolved_identities, resolved_aliases, resolved_records, resolved_relationships, trace
