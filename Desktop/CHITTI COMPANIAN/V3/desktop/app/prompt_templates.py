class PromptTemplates:
    """
    Central repository of prompt templates, organized by cognitive task.
    """
    
    INTENT_CLASSIFICATION = """{system_rules}

Current Session Context:
{session_context}

Working Memory:
{working_memory}

Recent Messages:
{recent_messages}

Classify the following user input into a single Intent.
Input: {user_input}

Respond strictly with a JSON object. Ensure it conforms to this schema:
{{
  "intent": "IntentName",
  "confidence": 0.0 to 1.0,
  "entities": {{}}
}}
"""

    PARAMETER_EXTRACTION = """{system_rules}
    
    Extract parameters from the user input based on the given intent...
    """

    CLARIFICATION = """
        The user's request is ambiguous. Review the provided context and generate exactly ONE targeted clarification question to resolve the ambiguity. 
        Generate the single question whose answer resolves the ambiguity with the highest information gain. If multiple ambiguities exist, ask only about the most blocking one.
        Do not provide a preamble or answer.
        Format your response as a JSON object:
        {
            "question": "Which John do you mean?",
            "target_parameter": "person_name",
            "confidence": 0.95
        }
    """

    RECOMMENDATION = """
        Based on the user's intent and context, recommend a list of candidate capabilities from the provided registry that could fulfill the request.
        Return ONLY valid JSON.
        For each capability include:
        - capability_name
        - confidence
        - extracted_parameters (dict of parameters you can confidently extract)
        - missing_parameters (list of required parameters that are missing)
        
        Do not invent capability names. If no capability fits, return [].
        
        Format your response as a JSON object:
        {
            "candidate_capabilities": [
                {
                    "capability_name": "ReminderCapability",
                    "confidence": 0.98,
                    "extracted_parameters": {"message": "Call Mom"},
                    "missing_parameters": ["time"],
                    "reason": "User asked to be reminded."
                }
            ],
            "confidence": 0.98,
            "reasoning": "The user explicitly asked for a reminder."
        }
    """
