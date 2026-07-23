from typing import List, Dict, Any
from desktop.models.experience import ExperienceDefinition, ExperienceEligibilityRule, IExperienceSectionProvider

class GreetingSection(IExperienceSectionProvider):
    def get_priority(self) -> int: return 10
    def build(self) -> Dict[str, Any]:
        return {"type": "greeting", "intent": "greet_morning"}

class WeatherSection(IExperienceSectionProvider):
    def get_priority(self) -> int: return 9
    def build(self) -> Dict[str, Any]:
        return {"type": "weather", "intent": "summarize_weather"}

class CalendarSection(IExperienceSectionProvider):
    def get_priority(self) -> int: return 8
    def build(self) -> Dict[str, Any]:
        return {"type": "calendar", "intent": "summarize_schedule"}

def get_morning_briefing_definition() -> ExperienceDefinition:
    """
    Sprint 7.7: Defines the Morning Briefing proactive experience with Scoring and Providers.
    """
    return ExperienceDefinition(
        id="exp_morning_briefing",
        name="Morning Briefing",
        triggers=["PresenceStateChanged"],
        eligibility_rules=[
            ExperienceEligibilityRule(
                rule_type="presence_state_includes",
                parameters={"state": "MORNING"},
                score_contribution=40
            ),
            ExperienceEligibilityRule(
                rule_type="presence_state_includes",
                parameters={"state": "AVAILABLE"},
                score_contribution=60
            )
        ],
        minimum_score=100,
        cooldown_seconds=43200, # 12 hours (only once a morning)
        priority=100,
        maximum_frequency=1,
        expiration=0,
        workflow_template="system.experience.morning_briefing"
    )

def compose_morning_briefing(providers: List[IExperienceSectionProvider]) -> Dict[str, Any]:
    # Sort providers by priority and build the workflow payload
    providers.sort(key=lambda p: p.get_priority(), reverse=True)
    sections = [p.build() for p in providers if p.get_eligibility_score() >= 0]
    return {"sections": sections}
