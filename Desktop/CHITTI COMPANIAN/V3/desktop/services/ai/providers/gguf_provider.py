import os
import json
import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class GGUFProvider:
    """
    Connects to a locally loaded GGUF model via llama-cpp-python.
    Includes auto-download logic from HuggingFace Hub.
    """
    def __init__(
        self, 
        repo_id: str = "Qwen/Qwen2.5-1.5B-Instruct-GGUF", 
        filename: str = "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        n_ctx: int = 4096,
        n_gpu_layers: int = 0  # Set > 0 for GPU acceleration if available
    ):
        self.repo_id = repo_id
        self.filename = filename
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.llm = None
        self.tools_schema = self._get_tools_schema()
        
    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
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
        
    def initialize(self):
        """
        Downloads the model if missing and loads it into memory via llama_cpp.
        """
        if self.llm is not None:
            return

        logger.info(f"Checking for GGUF model {self.filename} from {self.repo_id}...")
        
        try:
            local_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'models', 'llm')
            expected_path = os.path.abspath(os.path.join(local_dir, self.filename))
            
            if os.path.exists(expected_path):
                logger.info(f"Model found locally. Bypassing Hugging Face Hub check: {expected_path}")
                model_path = expected_path
            else:
                logger.info("Model not found locally. Downloading from Hugging Face Hub...")
                from huggingface_hub import hf_hub_download
                model_path = hf_hub_download(
                    repo_id=self.repo_id, 
                    filename=self.filename,
                    local_dir=local_dir
                )
                logger.info(f"Model path verified: {model_path}")
            
            from llama_cpp import Llama
            logger.info("Loading model into memory (llama_cpp)...")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            logger.info("GGUF model successfully loaded.")
        except ImportError:
            logger.error("Required packages missing. Run: pip install huggingface-hub llama-cpp-python")
        except Exception as e:
            logger.error(f"Failed to initialize GGUF provider: {e}")

    def generate(self, messages: List[Dict[str, str]], model: str = None, tools_enabled: bool = True) -> Dict[str, Any]:
        if self.llm is None:
            self.initialize()
            
        if self.llm is None:
            return {"text": "Error: GGUF LLM could not be initialized.", "tool_calls": []}

        kwargs = {
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3 if tools_enabled else 0.7,
        }
        
        if tools_enabled:
            kwargs["tools"] = self.tools_schema

        try:
            logger.info("GGUFProvider generating response...")
            response = self.llm.create_chat_completion(**kwargs)
            
            choice = response.get("choices", [{}])[0].get("message", {})
            text = choice.get("content", "") or ""
            
            # Extract tool calls if present (Llama-cpp-python maps them cleanly if the model supports it)
            tool_calls = choice.get("tool_calls", [])
            
            return {
                "text": text.strip(),
                "tool_calls": tool_calls
            }
        except Exception as e:
            logger.error(f"GGUFProvider generation failed: {e}")
            return {"text": "", "tool_calls": []}
