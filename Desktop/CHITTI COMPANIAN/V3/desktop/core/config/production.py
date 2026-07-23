"""
Production Configuration Module

Provides validated configuration using Pydantic Settings.
Supports environment-based configuration with type validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = "llama_cpp"
    model: str = "qwen2.5-1.5b"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    timeout: int = Field(default=60, ge=1)
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ["llama_cpp", "ollama", "openai", "gemini", "anthropic"]
        if v.lower() not in allowed:
            raise ValueError(f"Provider must be one of: {allowed}")
        return v.lower()


class SpeechConfig(BaseModel):
    """Speech processing configuration."""
    enabled: bool = False
    stt_provider: str = "whisper"
    tts_provider: str = "piper"
    language: str = Field(default="en", pattern="^[a-z]{2}(-[A-Z]{2})?$")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)


class SecurityConfig(BaseModel):
    """Security settings."""
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window: int = Field(default=60, ge=1)
    require_auth: bool = False
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    
    @field_validator('allowed_origins')
    @classmethod
    def validate_origins(cls, v: List[str]) -> List[str]:
        if "*" in v and len(v) > 1:
            raise ValueError("Cannot mix '*' with specific origins")
        return v


class HealthConfig(BaseModel):
    """Health check configuration."""
    enabled: bool = True
    endpoint: str = "/health"
    detailed: bool = False


class StorageConfig(BaseModel):
    """Storage configuration."""
    type: str = "sqlite"  # sqlite, memory, redis
    path: str = "storage/chitti.db"
    backup_enabled: bool = True
    backup_interval: int = Field(default=3600, ge=60)  # seconds


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/chitti.log"
    max_bytes: int = Field(default=10_000_000, ge=1_000_000)
    backup_count: int = Field(default=5, ge=1)


class RuntimeConfig(BaseModel):
    """Runtime behavior configuration."""
    max_concurrent_tasks: int = Field(default=10, ge=1)
    task_timeout: int = Field(default=300, ge=1)
    startup_timeout: int = Field(default=30, ge=1)
    shutdown_timeout: int = Field(default=10, ge=1)


class CHITTIConfig(BaseSettings):
    """
    Main CHITTI configuration with environment variable support.
    
    Supports loading from:
    - Environment variables (prefix: CHITTI_)
    - .env file
    - Default values
    
    Example .env:
        CHITTI_LLM__PROVIDER=ollama
        CHITTI_LLM__MODEL=mistral
        CHITTI_SPEECH__ENABLED=true
    """
    model_config = SettingsConfigDict(
        env_prefix="CHITTI_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars
    )
    
    # Application
    app_name: str = "CHITTI"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # Feature flags
    use_llm: bool = True
    use_speech: bool = False
    use_vision: bool = False
    
    # Subsystems
    llm: LLMConfig = Field(default_factory=LLMConfig)
    speech: SpeechConfig = Field(default_factory=SpeechConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    
    # Transport
    transport: str = "default"  # default, cli, websocket, http
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    def validate_for_production(self) -> List[str]:
        """
        Validate configuration for production deployment.
        Returns list of warnings (empty if production-ready).
        """
        warnings = []
        
        if not self.is_production:
            warnings.append("Not running in production mode")
        
        if self.debug:
            warnings.append("Debug mode is enabled")
        
        if not self.security.require_auth:
            warnings.append("Authentication is not required")
        
        if self.logging.level == "DEBUG":
            warnings.append("Debug logging enabled")
        
        if self.storage.type == "memory":
            warnings.append("Using in-memory storage - data will not persist")
        
        if self.runtime.max_concurrent_tasks > 50:
            warnings.append("High concurrency setting may cause resource issues")
        
        return warnings


# Global config instance (lazy loaded)
_config: Optional[CHITTIConfig] = None


def get_config() -> CHITTIConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = CHITTIConfig()
    return _config


def reload_config() -> CHITTIConfig:
    """Reload configuration from environment."""
    global _config
    _config = CHITTIConfig()
    return _config
