import json
from desktop.models.inference import InferenceResponse, InferenceResult

class InferenceValidator:
    """
    Acts as a firewall between LLM providers and the Cognitive Pipeline.
    Normalizes provider outputs, validates schemas, and clamps confidences.
    (Rule 186: Provider Diversity Shall Not Affect Planning)
    """
    
    def validate(self, response: InferenceResponse) -> InferenceResult:
        try:
            data = json.loads(response.content)
            
            intent = data.get("intent", "UnknownIntent")
            
            # Clamp confidence to 0.0 - 1.0
            try:
                raw_conf = float(data.get("confidence", 0.0))
                confidence = max(0.0, min(1.0, raw_conf))
            except (ValueError, TypeError):
                confidence = 0.0
                
            entities = data.get("entities", {})
            if not isinstance(entities, dict):
                entities = {}
                
            return InferenceResult(
                intent=intent,
                confidence=confidence,
                entities=entities,
                raw_response=response.content,
                reasoning_notes=f"Validated from {response.model_used}"
            )
            
        except json.JSONDecodeError as e:
            # Shield the planner from malformed JSON
            print(f"[InferenceValidator] ❌ Malformed JSON from {response.model_used}: {e}")
            return InferenceResult(
                intent="UnknownIntent",
                confidence=0.0,
                entities={},
                raw_response=response.content,
                reasoning_notes=f"JSONDecodeError: {e}"
            )
        except Exception as e:
            print(f"[InferenceValidator] ❌ Unknown Error: {e}")
            return InferenceResult(
                intent="UnknownIntent",
                confidence=0.0,
                entities={},
                raw_response=response.content,
                reasoning_notes=f"Error: {e}"
            )
