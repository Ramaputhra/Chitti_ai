import logging
import requests
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class OllamaProvider:
    """
    Connects to a local Ollama instance (e.g. qwen2.5, gemma2).
    """
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.2"):
        self.base_url = base_url
        self.default_model = default_model
        
    def generate(self, messages: List[Dict[str, str]], model: str = None, tools_enabled: bool = True) -> Dict[str, Any]:
        model_name = model or self.default_model
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "application.launch",
                    "description": "Opens a desktop application by name (e.g. Chrome, VS Code, Notepad).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "application": {
                                "type": "string",
                                "description": "The name of the application to open."
                            }
                        },
                        "required": ["application"]
                    }
                }
            }
        ]
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3, # lower temp for tools
                "num_ctx": 4096
            }
        }
        if tools_enabled:
            payload["tools"] = tools
        
        try:
            logger.info(f"OllamaProvider generating with model: {model_name}")
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            message = data.get("message", {})
            return {
                "text": message.get("content", "").strip(),
                "tool_calls": message.get("tool_calls", [])
            }
        except Exception as e:
            logger.error(f"OllamaProvider generation failed: {e}")
            raise e
