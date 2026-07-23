import os
import json
import logging
from typing import Any, List, Dict, Generator
from desktop.platform.shared.interfaces.llm import ILLMProvider, HealthStatus

logger = logging.getLogger(__name__)

class ModelNotInstalledError(Exception):
    pass

class LlamaCppProvider(ILLMProvider):
    """
    Connects to a locally loaded GGUF model via llama-cpp-python.
    This provider assumes the model has already been verified and downloaded 
    by the Model Manager. Configured via inference.json.
    """
    def __init__(self):
        self.llm = None
        self._is_loaded = False
        self.last_error = None
        
        # Load configuration from platform
        self.config_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'desktop', 'platform', 'configuration', 'inference.json'
        ))
        self.config = self._load_config()
        
        self.model_name = self.config.get("default_model", "qwen2.5-1.5b-instruct")
        self.n_ctx = self.config.get("context_size", 4096)
        self.n_gpu_layers = self.config.get("gpu_layers", 0)
        self.n_threads = self.config.get("threads", 4)
        self.batch_size = self.config.get("batch_size", 512)
        
        # Absolute path calculation for assets
        self.model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'models', 'llm', self.model_name, 'model.gguf'
        ))
        
        self.tools_schema = self._get_tools_schema()
        
    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {self.config_path}: {e}")
        return {}

    @property
    def name(self) -> str:
        return "LlamaCppProvider"

    def capabilities(self) -> List[str]:
        return [
            "Chat",
            "Tool Calling",
            "JSON Mode",
            f"Context Length: {self.n_ctx}",
            "Streaming"
        ]

    def health_check(self) -> HealthStatus:
        status = "HEALTHY" if self._is_loaded else "FAILED"
        if not self._is_loaded and not self.last_error:
            status = "DEGRADED"  # Not loaded yet, but no explicit error
            
        return HealthStatus(
            status=status,
            loaded_model=self.model_name,
            context_size=self.n_ctx,
            gpu_enabled=self.n_gpu_layers > 0,
            memory_usage=None,  # Requires psutil or similar
            last_error=self.last_error
        )

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
        Loads the model into memory via llama_cpp. Throws ModelNotInstalledError if file missing.
        """
        if self._is_loaded:
            return

        logger.info(f"[{self.name}] Initializing model from {self.model_path}...")
        
        if not os.path.exists(self.model_path):
            self.last_error = f"Model file not found at {self.model_path}"
            logger.error(f"[{self.name}] {self.last_error}")
            raise ModelNotInstalledError(self.last_error)
            
        try:
            from llama_cpp import Llama
            logger.info(f"[{self.name}] Loading model into memory...")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                n_threads=self.n_threads,
                n_batch=self.batch_size,
                verbose=False
            )
            self._is_loaded = True
            self.last_error = None
            logger.info(f"[{self.name}] Model successfully loaded.")
            
        except ImportError:
            self.last_error = "llama-cpp-python not installed."
            logger.error(f"[{self.name}] {self.last_error}")
            raise
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"[{self.name}] Failed to initialize provider: {e}")
            raise

    def generate(self, messages: List[Dict[str, str]], model: str = None, tools_enabled: bool = True) -> Dict[str, Any]:
        if not self._is_loaded or self.llm is None:
            self.initialize()
            
        kwargs = {
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3 if tools_enabled else 0.7,
        }
        
        if tools_enabled:
            kwargs["tools"] = self.tools_schema

        try:
            logger.info(f"[{self.name}] Generating response...")
            response = self.llm.create_chat_completion(**kwargs)
            
            choice = response.get("choices", [{}])[0].get("message", {})
            text = choice.get("content", "") or ""
            
            # Extract tool calls if present
            tool_calls = choice.get("tool_calls", [])
            
            return {
                "text": text.strip(),
                "tool_calls": tool_calls
            }
        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            return {"text": "", "tool_calls": []}

    def generate_stream(self, messages: List[Dict[str, str]], tools_enabled: bool = True) -> Generator[Dict[str, Any], None, None]:
        if not self._is_loaded or self.llm is None:
            self.initialize()
            
        kwargs = {
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3 if tools_enabled else 0.7,
            "stream": True
        }
        
        if tools_enabled:
            kwargs["tools"] = self.tools_schema

        try:
            logger.info(f"[{self.name}] Starting stream...")
            yield {"event": "StreamStarted"}
            
            response_stream = self.llm.create_chat_completion(**kwargs)
            
            for chunk in response_stream:
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if "content" in delta and delta["content"]:
                    yield {"event": "TokenGenerated", "token": delta["content"]}
                elif "tool_calls" in delta and delta["tool_calls"]:
                    # Basic stream event translation for tool calls
                    yield {"event": "ToolCallStarted", "tool": delta["tool_calls"]}
                    yield {"event": "ToolCallFinished"}
                    
            yield {"event": "StreamCompleted"}
            
        except Exception as e:
            logger.error(f"[{self.name}] Stream failed: {e}")
            yield {"event": "StreamCompleted", "error": str(e)}

    # Stub implementations to satisfy the base class ILLMProvider abstract methods
    def list_models(self) -> List[str]:
        return [self.model_name]

    def stream(self, request: Any) -> Generator[Any, None, None]:
        pass

    def complete(self, request: Any) -> Any:
        pass
