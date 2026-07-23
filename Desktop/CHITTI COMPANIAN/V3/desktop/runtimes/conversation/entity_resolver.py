import re
from typing import Optional, List, Tuple
from desktop.models.conversation import ConversationSession, EntityDescriptor, ResolvedInteraction

class EntityResolver:
    """
    Deterministically resolves ambiguous references (pronouns like "it", "that") 
    before the language model attempts to parse intents using confidence scoring.
    """
    
    PRONOUNS = [r'\bit\b', r'\bthat\b', r'\bthis\b', r'\bthem\b', r'\bapplication\b', r'\bapp\b', r'\bprogram\b']
    
    @classmethod
    def resolve(cls, text: str, session: ConversationSession) -> ResolvedInteraction:
        """
        Scans for pronouns or ambiguous nouns and resolves them to the best entity.
        Returns a structured ResolvedInteraction without mutating the original text (Rule 87).
        """
        if not session.recent_entities:
            return ResolvedInteraction(original_text=text, resolved_text=text, resolved_entities=[])
            
        best_entity = cls._select_best_entity(text, session)
        if not best_entity:
            return ResolvedInteraction(original_text=text, resolved_text=text, resolved_entities=[])
            
        resolved_entities = []
        for pronoun_pattern in cls.PRONOUNS:
            if re.search(pronoun_pattern, text, flags=re.IGNORECASE):
                resolved_entities.append(best_entity)
                break
            
        return ResolvedInteraction(
            original_text=text,
            resolved_text=text,
            resolved_entities=resolved_entities
        )
        
    @classmethod
    def _select_best_entity(cls, text: str, session: ConversationSession) -> Optional[EntityDescriptor]:
        """Selects the entity with the highest confidence score."""
        if not session.recent_entities:
            return None
            
        scored_entities: List[Tuple[EntityDescriptor, float]] = []
        
        for idx, entity in enumerate(session.recent_entities):
            score = 0.0
            
            # Recency factor (more recent = higher base score)
            # recent_entities is ordered oldest to newest
            recency_bonus = (idx + 1) / len(session.recent_entities) * 0.5
            score += recency_bonus
            
            # Explicit mention
            if entity.display.lower() in text.lower():
                score += 0.4
                
            # Focus/Activity context
            if session.companion_context.focus and session.companion_context.focus.lower() in entity.display.lower():
                score += 0.3
                
            # Execution success boost
            if session.execution_context.last_success:
                last_exec_payload = session.execution_context.last_success
                if str(last_exec_payload.get("app_command", "")).lower() == str(entity.executable).lower():
                    score += 0.2
                    
            scored_entities.append((entity, score))
            
        # Sort by score descending
        scored_entities.sort(key=lambda x: x[1], reverse=True)
        return scored_entities[0][0] if scored_entities else None
