from desktop.personality.runtime.personality_state import PersonalityProfile

class UIPersonalityAdapter:
    """
    S36A-R1: Adapts Desktop UI notification and badge wording according to active PersonalityProfile.
    """
    UI_WORDING_MAP = {
        "Reminder Created": {
            "professional": "Reminder scheduled.",
            "friendly": "Done boss! I'll remind you.",
            "humorous": "Future-you says don't forget this 😄",
            "minimal": "Reminder set."
        },
        "Browser Opened": {
            "professional": "Browser opened.",
            "friendly": "Browser ready, boss!",
            "humorous": "Time to surf the web 🌐",
            "minimal": "Opened."
        },
        "System Error": {
            "professional": "An error has occurred.",
            "friendly": "Oops! Ran into a small hiccup.",
            "humorous": "Whoops, something blew up 💥",
            "minimal": "Error."
        }
    }

    def adapt_ui_text(self, profile: PersonalityProfile, key: str, default_text: str) -> str:
        if key in self.UI_WORDING_MAP:
            mapping = self.UI_WORDING_MAP[key]
            if profile.concise > 0.8:
                return mapping.get("minimal", default_text)
            if profile.professional > 0.8:
                return mapping.get("professional", default_text)
            if profile.humorous > 0.7:
                return mapping.get("humorous", default_text)
            if profile.friendly > 0.6:
                return mapping.get("friendly", default_text)
        return default_text
