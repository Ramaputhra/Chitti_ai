from desktop.personality.runtime.personality_state import PersonalityProfile
from desktop.personality.runtime.narration_context import NarrationContext
from desktop.personality.runtime.narration_rules import NarrationRules

class NarrationStyleEngine:
    """
    S36A-R1: Rewrites LLM response texts according to the active PersonalityProfile and NarrationContext.
    """
    def __init__(self):
        self.rules = NarrationRules()

    def rewrite_narration(
        self,
        text: str,
        profile: PersonalityProfile,
        context: Optional[NarrationContext] = None
    ) -> str:
        ctx = context or NarrationContext()

        # Check for exact rule match first
        rule_text = self.rules.get_rule_text(ctx.domain_intent, self._determine_style_mode(profile))
        if rule_text:
            return rule_text

        # Dynamic rewrite based on traits
        if profile.concise > 0.8:
            # Minimal style
            clean = text.strip()
            if clean.startswith("I have "):
                clean = clean.replace("I have ", "")
            return clean

        if profile.motivational > 0.8:
            return f"Let's do it! {text}"

        if profile.friendly > 0.7:
            if not text.startswith("Right on it") and not text.startswith("Hey"):
                return f"Right on it, {text.lower() if text[0].isupper() else text}"

        return text

    def _determine_style_mode(self, profile: PersonalityProfile) -> str:
        if profile.concise > 0.8:
            return "minimal"
        if profile.professional > 0.8:
            return "professional"
        if profile.motivational > 0.8:
            return "motivational"
        if profile.humorous > 0.7:
            return "humorous"
        return "friendly"
