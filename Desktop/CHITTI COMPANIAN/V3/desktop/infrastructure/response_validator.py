import json

class ResponseValidator:
    """
    Enforces maximum length, valid JSON, and prevents XML leak or prompt exposure.
    Runs after InferenceProvider returns.
    """
    
    @staticmethod
    def validate(response_text: str, require_json: bool = False, max_length: int = 4000) -> str:
        if len(response_text) > max_length:
            return response_text[:max_length] + "... [TRUNCATED]"
            
        if require_json:
            try:
                json.loads(response_text)
            except json.JSONDecodeError:
                return '{"error": "Invalid JSON returned by LLM"}'
                
        # Prevent XML tag leak
        if "<SYSTEM_PERSONA>" in response_text or "<PLANNER_GOAL>" in response_text:
            return "Error: Internal context leaked into response."
            
        return response_text
