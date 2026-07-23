import re
from typing import Optional, List, Tuple
from desktop.models.conversation import ConversationSession, EntityDescriptor, ResolvedInteraction, ConversationFocus, ConversationArtifact

class ConversationResolver:
    """
    Deterministically resolves conversational context across three stages:
    1. Entity Resolution
    2. Artifact Resolution
    3. Follow-up Resolution
    Complies with Rule 246 (Conversation Context Expansion).
    """
    
    PRONOUNS = [r'\bit\b', r'\bthat\b', r'\bthis\b', r'\bthose\b', r'\bthem\b', r'\bprevious project\b', r'\bapplication\b', r'\bapp\b']

    @classmethod
    def resolve(cls, text: str, focus: ConversationFocus, session: ConversationSession) -> ResolvedInteraction:
        """
        Executes the full 3-stage resolution pipeline.
        Returns a structured ResolvedInteraction.
        """
        # Initialize with raw text
        resolved_text = text
        resolved_entities = []
        
        # Stage 1: Entity Resolution
        resolved_text, entities = cls._resolve_entities(resolved_text, session)
        resolved_entities.extend(entities)
        
        # Stage 2: Artifact Resolution & Stage 3: Follow-up Resolution
        routing_action, expanded_text = cls._resolve_followups(resolved_text, focus)
        if routing_action:
            resolved_text = expanded_text
            
        return ResolvedInteraction(
            original_text=text,
            resolved_text=resolved_text,
            resolved_entities=resolved_entities,
            routing_action=routing_action
        )

    @classmethod
    def _resolve_entities(cls, text: str, session: ConversationSession) -> Tuple[str, List[EntityDescriptor]]:
        """Stage 1: Resolve explicit pronouns to entities."""
        if not session.recent_entities:
            return text, []
            
        # Select best entity based on recency
        best_entity = session.recent_entities[-1]
        
        resolved_text = text
        matched_entities = []
        
        for pronoun_pattern in cls.PRONOUNS:
            if re.search(pronoun_pattern, text, flags=re.IGNORECASE):
                resolved_text = re.sub(pronoun_pattern, best_entity.display, text, flags=re.IGNORECASE)
                matched_entities.append(best_entity)
                break
                
        return resolved_text, matched_entities

    @classmethod
    def _resolve_followups(cls, text: str, focus: ConversationFocus) -> Tuple[Optional[str], str]:
        """
        Stage 2 & 3: Match conversational continuations to Artifact Affordances.
        Returns (routing_action, expanded_text).
        """
        if not focus.current_conversation_artifact:
            return None, text
            
        artifact = focus.current_conversation_artifact
        lower_text = text.lower().strip()
        
        # Follow-up keywords mapped to potential affordances
        followup_mapping = {
            "show me": "Presentation",
            "show me.": "Presentation",
            "open it": "Presentation",
            "navigate": "Navigation",
            "navigate.": "Navigation",
            "traffic": "Traffic",
            "routes": "Routes",
            "why?": "Explain",
            "why": "Explain",
            "explain": "Explain",
            "tell me more": "Explain",
            "tell me more.": "Explain",
            "open result": "Open Result",
            "open second result": "Open Result",
            "open second result.": "Open Result",
            "compare": "Compare",
            "compare.": "Compare",
            "summarize": "Summarize",
            "open product": "Open Product",
            "buy": "Buy",
            "buy this one": "Buy",
            "buy this one.": "Buy",
            "wishlist": "Wishlist",
            "highlight": "Highlight",
            "highlight.": "Highlight",
            "translate": "Translate",
            "translate.": "Translate",
            "copy": "Copy",
            "execute": "Execute",
            "modify": "Modify",
            "cancel": "Cancel",
            "continue": "Continue",
            "continue.": "Continue"
        }
        
        # Simple exact match for follow-ups for now
        matched_affordance = followup_mapping.get(lower_text)
        
        if matched_affordance and matched_affordance in artifact.supported_followup_actions:
            # We have a valid affordance follow-up. 
            expanded = f"{matched_affordance} {artifact.artifact_type} ({artifact.summary})"
            return matched_affordance, expanded
            
        return None, text
