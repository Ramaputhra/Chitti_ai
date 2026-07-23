from typing import List, Dict

class InferenceContext:
    def __init__(self, max_history_turns: int = 4):
        self.max_history_turns = max_history_turns
        self.history: List[Dict[str, str]] = []
        
        self.system_prompt = (
            "You are CHITTI. You are a friendly desktop companion.\n"
            "Respond conversationally.\n"
            "Keep answers concise unless the user requests detail.\n"
            "Do not invent desktop actions.\n"
            "CRITICAL: If the user is just saying hello or asking a question, DO NOT use any tools. Only use tools if explicitly asked to perform an action.\n"
            "Do not claim to have completed actions you haven't performed."
        )

    def add_turn(self, user_text: str, assistant_response: str):
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": assistant_response})
        
        # Keep only the last `max_history_turns` pairs (i.e. length * 2)
        max_len = self.max_history_turns * 2
        if len(self.history) > max_len:
            self.history = self.history[-max_len:]

    def build_prompt(self, current_transcript: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        
        # Check if it's a structured contextual prompt from ConversationRuntime
        import json
        try:
            if current_transcript.strip().startswith("{"):
                data = json.loads(current_transcript)
                if "system_directive" in data:
                    messages[0]["content"] += f"\n\nContextual Directive: {data.pop('system_directive')}"
                messages.append({"role": "user", "content": f"Execution Evidence: {json.dumps(data)}"})
                return messages
        except json.JSONDecodeError:
            pass
            
        messages.append({"role": "user", "content": current_transcript})
        return messages
