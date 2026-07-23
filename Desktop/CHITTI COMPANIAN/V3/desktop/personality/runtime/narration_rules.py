from typing import Dict

class NarrationRules:
    """
    S36A-R1: Rule engine providing template rewrites for Greetings, Confirmations, Errors, Warnings, Celebrations, Reminders, Navigation, Browser, Vision, Presentation.
    """
    RULES: Dict[str, Dict[str, str]] = {
        "OPEN_BROWSER": {
            "professional": "Opening your browser.",
            "friendly": "Right on it boss, opening your browser.",
            "minimal": "Browser opened.",
            "motivational": "Let's do it! Opening your browser."
        },
        "REMINDER_CREATE": {
            "professional": "Reminder scheduled.",
            "friendly": "Done boss! I'll remind you.",
            "minimal": "Reminder set.",
            "humorous": "Future-you says don't forget this 😄"
        },
        "GREETING": {
            "professional": "Good day. How may I assist you?",
            "friendly": "Hey boss! Ready whenever you are.",
            "minimal": "Ready.",
            "motivational": "Let me know what we're conquering today!"
        },
        "SYSTEM_SUCCESS": {
            "professional": "Action completed successfully.",
            "friendly": "All done boss! Looks awesome.",
            "minimal": "Success.",
            "motivational": "Boom! Nailed it!"
        }
    }

    def get_rule_text(self, rule_key: str, style_mode: str) -> str:
        key = rule_key.upper()
        mode = style_mode.lower()
        if key in self.RULES and mode in self.RULES[key]:
            return self.RULES[key][mode]
        return ""
