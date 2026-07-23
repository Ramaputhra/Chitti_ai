import logging
from typing import Dict, Any, Optional

from desktop.models.remote_provider import RemoteRequest, RetryPolicy, ProviderState
from desktop.platform.ai.remote_registry import RemoteProviderRegistry
from desktop.platform.ai.providers.openrouter import OpenRouterAdapter

logger = logging.getLogger(__name__)

class RemoteRuntime:
    """
    Stateless execution engine for remote providers (Cloud, LAN, MCP).
    DOES NOT STORE: Conversation, Memory, History, Cache, Plans.
    ONLY STORES: Session, Headers, HTTP, Retries (via Adapters/Session).
    """
    def __init__(self, registry: RemoteProviderRegistry):
        self.registry = registry
        # In a full implementation, adapters would be instantiated via a factory
        # based on the manifests in the registry.
        self._adapters: Dict[str, Any] = {}

    def bind_adapter(self, provider_id: str, adapter: Any) -> None:
        """Bind an instantiated adapter to a registered provider ID."""
        if self.registry.get_provider(provider_id):
            self._adapters[provider_id] = adapter
            adapter.warm()

    def execute(self, provider_id: str, request: RemoteRequest) -> Dict[str, Any]:
        """
        Executes a request against the specified remote provider.
        Enforces RetryPolicies and capability checks before hitting the adapter.
        """
        adapter = self._adapters.get(provider_id)
        if not adapter:
            raise ValueError(f"No adapter bound for provider: {provider_id}")

        manifest = self.registry.get_provider(provider_id)
        
        # 1. Capability Discovery Check
        if request.service == "vision" and not manifest.capabilities.vision:
            logger.error(f"Request rejected: Provider {provider_id} lacks vision capability.")
            raise ValueError(f"Provider {provider_id} does not support vision.")
            
        # 2. Execution with Retry Policy
        attempts = 0
        max_attempts = 1
        
        if request.retry_policy in (RetryPolicy.SAFE, RetryPolicy.IDEMPOTENT):
            max_attempts = 3
            
        last_exception = None
        
        while attempts < max_attempts:
            try:
                # The adapter's session circuit breaker will raise ConnectionError if open
                return adapter.execute(request)
            except ConnectionError as ce:
                logger.warning(f"Network error on attempt {attempts + 1}: {ce}")
                last_exception = ce
            except Exception as e:
                logger.error(f"Unexpected execution error: {e}")
                last_exception = e
                # Do not retry on non-network/circuit-breaker errors unless specific handling
                break
                
            attempts += 1
            
        logger.error(f"Execution failed after {attempts} attempts. Policy: {request.retry_policy.value}")
        raise last_exception or RuntimeError("Execution failed")
