import asyncio
from desktop.runtimes.conversation.conversation_resolver import ConversationResolver
from desktop.models.conversation import ConversationSession, ConversationFocus, ConversationArtifact, EntityDescriptor
from datetime import datetime

def run_tests():
    print("--- Running Sprint 18.5 Conversation Intelligence Regression Suite ---")
    
    session = ConversationSession(session_id="test_session")
    
    # Setup mock active artifact (Navigation)
    art1 = ConversationArtifact(
        artifact_id="nav_1",
        artifact_type="NavigationResult",
        capability_id="nav_cap",
        timestamp=datetime.now(),
        summary="Route to Paris",
        structured_result={"destination": "Paris"},
        referenced_entities=[],
        supported_followup_actions=["Presentation", "Navigation", "Traffic", "Routes", "Explain"],
        presentation_available=True,
        expiration_policy="session",
        confidence=1.0
    )
    session.focus.current_conversation_artifact = art1
    
    # 1. Pronoun Resolution
    session.recent_entities.append(EntityDescriptor(id="app_calculator", display="calculator", type="application"))
    res = ConversationResolver.resolve("close it", session.focus, session)
    print(f"[Pronoun] 'close it' -> {res.resolved_text}")
    assert "calculator" in res.resolved_text
    
    # 2. Context Expansion / Presentation Routing
    res = ConversationResolver.resolve("show me", session.focus, session)
    print(f"[Context Routing] 'show me' -> Action: {res.routing_action}, Expanded: {res.resolved_text}")
    assert res.routing_action == "Presentation"
    
    # 3. Follow-up Explanation
    res = ConversationResolver.resolve("why?", session.focus, session)
    print(f"[Explanation] 'why?' -> Action: {res.routing_action}, Expanded: {res.resolved_text}")
    assert res.routing_action == "Explain"
    
    # 4. Amazon Follow-up
    art2 = ConversationArtifact(
        artifact_id="amzn_1",
        artifact_type="AmazonSearchResult",
        capability_id="shop_cap",
        timestamp=datetime.now(),
        summary="Laptop results",
        structured_result={},
        referenced_entities=[],
        supported_followup_actions=["Wishlist", "Open Product", "Compare", "Buy", "Explain"],
        presentation_available=True,
        expiration_policy="session",
        confidence=1.0
    )
    session.focus.current_conversation_artifact = art2
    res = ConversationResolver.resolve("buy this one", session.focus, session)
    print(f"[Shopping] 'buy this one' -> Action: {res.routing_action}, Expanded: {res.resolved_text}")
    assert res.routing_action == "Buy"
    
    # 5. Clarification Fallback
    res = ConversationResolver.resolve("do something weird", session.focus, session)
    print(f"[Fallback] 'do something weird' -> Action: {res.routing_action}")
    assert res.routing_action is None
    
    print("\n✓ Pronoun Resolution")
    print("✓ Context Expansion")
    print("✓ Artifact Reuse")
    print("✓ Shopping Workflow Continuation")
    print("✓ Presentation Routing")
    print("✓ Clarification fallback")
    print("\nAll minimum scenarios passed!")

if __name__ == "__main__":
    run_tests()
