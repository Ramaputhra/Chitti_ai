from typing import Dict, Any
from desktop.platform.providers.base import BaseProvider

class ProviderHealth:
    """
    Evaluates provider availability, dependencies, and health indicators.
    """
    @staticmethod
    def check_health(provider: BaseProvider) -> Dict[str, Any]:
        try:
            health = provider.health_check()
            return health
        except Exception as e:
            return {
                "healthy": False,
                "status_code": 500,
                "provider_id": provider.provider_id,
                "error": str(e)
            }

    @staticmethod
    def is_available(provider: BaseProvider) -> bool:
        health = ProviderHealth.check_health(provider)
        return health.get("healthy", False)
