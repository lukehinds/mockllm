import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from .providers.base import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class ProviderMetadata:
    name: str
    version: str = "1.0.0"
    description: str = ""
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    supported_models: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    config_schema: Optional[Dict[str, Any]] = None


class ProviderRegistry:
    _instance = None
    _providers: Dict[str, Type[LLMProvider]] = {}
    _metadata: Dict[str, ProviderMetadata] = {}
    _initialized_providers: Dict[str, LLMProvider] = {}

    def __new__(cls) -> "ProviderRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(
        cls,
        name: str,
        metadata: Optional[ProviderMetadata] = None,
    ) -> Callable[[Type[LLMProvider]], Type[LLMProvider]]:
        def decorator(provider_class: Type[LLMProvider]) -> Type[LLMProvider]:
            cls._providers[name] = provider_class
            if metadata:
                cls._metadata[name] = metadata
            else:
                cls._metadata[name] = ProviderMetadata(name=name)
            logger.info(f"Registered provider: {name}")
            return provider_class

        return decorator

    @classmethod
    def get_provider_class(cls, name: str) -> Optional[Type[LLMProvider]]:
        return cls._providers.get(name)

    @classmethod
    def get_provider(cls, name: str, config: Any) -> Optional[LLMProvider]:
        if name not in cls._initialized_providers:
            provider_class = cls.get_provider_class(name)
            if provider_class:
                cls._initialized_providers[name] = provider_class(config)
        return cls._initialized_providers.get(name)

    @classmethod
    def get_metadata(cls, name: str) -> Optional[ProviderMetadata]:
        return cls._metadata.get(name)

    @classmethod
    def list_providers(cls) -> List[str]:
        return list(cls._providers.keys())

    @classmethod
    def get_all_endpoints(cls) -> Dict[str, List[Dict[str, Any]]]:
        endpoints: Dict[str, List[Dict[str, Any]]] = {}
        for provider_name, metadata in cls._metadata.items():
            for endpoint in metadata.endpoints:
                path = endpoint.get("path", "")
                if path not in endpoints:
                    endpoints[path] = []
                endpoints[path].append(
                    {
                        "provider": provider_name,
                        "method": endpoint.get("method", "POST"),
                        "handler": endpoint.get("handler", "handle_chat_completion"),
                    }
                )
        return endpoints

    @classmethod
    def clear(cls) -> None:
        cls._providers.clear()
        cls._metadata.clear()
        cls._initialized_providers.clear()


def register_provider(
    name: str,
    version: str = "1.0.0",
    description: str = "",
    endpoints: Optional[List[Dict[str, Any]]] = None,
    supported_models: Optional[List[str]] = None,
    capabilities: Optional[Dict[str, Any]] = None,
) -> Callable[[Type[LLMProvider]], Type[LLMProvider]]:
    metadata = ProviderMetadata(
        name=name,
        version=version,
        description=description,
        endpoints=endpoints or [],
        supported_models=supported_models or [],
        capabilities=capabilities or {},
    )
    return ProviderRegistry.register(name, metadata)
