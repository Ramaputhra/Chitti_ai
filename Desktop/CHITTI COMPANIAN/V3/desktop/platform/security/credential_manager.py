import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """
    Securely stores and retrieves API keys using the OS-level credential store.
    On Windows, this interfaces with DPAPI / Windows Credential Manager.
    Keys are NEVER stored in SQLite, Memory Runtime, or JSON configs.
    """
    
    def __init__(self, namespace: str = "chitti_ai_system"):
        self.namespace = namespace
        self._keyring_available = False
        
        try:
            import keyring
            self._keyring_available = True
        except ImportError:
            logger.warning("Keyring module not installed. CredentialManager will use an insecure dev fallback. RUN: pip install keyring")
            self._dev_cache = {}

    def save_credential(self, service_name: str, api_key: str) -> bool:
        """Saves an API key securely."""
        if not api_key:
            return False
            
        if self._keyring_available:
            import keyring
            try:
                keyring.set_password(self.namespace, service_name, api_key)
                return True
            except Exception as e:
                logger.error(f"Failed to save credential for {service_name}: {e}")
                return False
        else:
            self._dev_cache[service_name] = api_key
            return True

    def get_credential(self, service_name: str) -> str:
        """Retrieves an API key securely."""
        if self._keyring_available:
            import keyring
            try:
                return keyring.get_password(self.namespace, service_name)
            except Exception as e:
                logger.error(f"Failed to retrieve credential for {service_name}: {e}")
                return None
        else:
            return self._dev_cache.get(service_name)
            
    def remove_credential(self, service_name: str) -> bool:
        """Deletes an API key securely."""
        if self._keyring_available:
            import keyring
            try:
                keyring.delete_password(self.namespace, service_name)
                return True
            except Exception as e:
                logger.error(f"Failed to delete credential for {service_name}: {e}")
                return False
        else:
            if service_name in self._dev_cache:
                del self._dev_cache[service_name]
            return True
