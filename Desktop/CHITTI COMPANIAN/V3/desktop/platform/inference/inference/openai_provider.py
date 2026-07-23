import os
import time
import requests
from desktop.app.inference_contracts import ILLMProvider
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderInfo, ProviderCapabilities, ProviderHealth, CapabilityType, CapabilityMetadata, CapabilityStatus

class OpenAIProvider(ILLMProvider):
    """
    Real cloud LLM Provider via OpenAI's REST API.
    """
    def __init__(self, api_key: str = None, default_model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.default_model = default_model
        
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="OpenAIProvider",
            model=self.default_model,
            capabilities=ProviderCapabilities(
                capabilities={
                    CapabilityType.STRUCTURED_OUTPUT: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.STREAMING: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.MULTIMODAL: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.FUNCTION_CALLING: CapabilityMetadata(CapabilityStatus.NATIVE),
                },
                max_context=128000,
                is_local=False
            )
        )
        
    def health(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth.UNAVAILABLE
        # A lightweight way to check health would be fetching models list or just assuming ready if API key exists.
        # We will assume READY if we have an API key.
        return ProviderHealth.READY

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        if not self.api_key:
            raise Exception("OpenAI API key not provided.")
            
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
            
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": request.model_hint or self.default_model,
            "messages": messages,
            "temperature": request.temperature
        }
        
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        import asyncio
        response = await asyncio.to_thread(
            requests.post, 
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload, 
            timeout=request.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        latency = (time.time() - start_time) * 1000
        
        content = data["choices"][0]["message"].get("content", "")
        
        return InferenceResponse(
            content=content,
            model_used=data.get("model", self.default_model),
            latency_ms=latency,
            usage=data.get("usage", {})
        )
