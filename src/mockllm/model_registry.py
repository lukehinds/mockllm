from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModelInfo:
    name: str
    provider: str
    aliases: List[str] = field(default_factory=list)
    context_window: int = 4096
    max_tokens: Optional[int] = None
    capabilities: Dict[str, bool] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    _instance = None
    _models: Dict[str, ModelInfo] = {}
    _aliases: Dict[str, str] = {}

    def __new__(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_default_models()
        return cls._instance

    def _initialize_default_models(self) -> None:
        default_models = [
            ModelInfo(
                name="gpt-3.5-turbo",
                provider="openai",
                aliases=["gpt-3.5", "turbo"],
                context_window=4096,
                max_tokens=4096,
                capabilities={"streaming": True, "function_calling": True},
            ),
            ModelInfo(
                name="gpt-4",
                provider="openai",
                aliases=["gpt-4-0613"],
                context_window=8192,
                max_tokens=8192,
                capabilities={
                    "streaming": True,
                    "function_calling": True,
                    "vision": False,
                },
            ),
            ModelInfo(
                name="gpt-4-turbo",
                provider="openai",
                aliases=["gpt-4-turbo-preview", "gpt-4-1106"],
                context_window=128000,
                max_tokens=4096,
                capabilities={
                    "streaming": True,
                    "function_calling": True,
                    "vision": True,
                },
            ),
            ModelInfo(
                name="claude-3-sonnet-20240229",
                provider="anthropic",
                aliases=["claude-3-sonnet", "sonnet"],
                context_window=200000,
                max_tokens=4096,
                capabilities={"streaming": True, "vision": True},
            ),
            ModelInfo(
                name="claude-3-opus-20240229",
                provider="anthropic",
                aliases=["claude-3-opus", "opus"],
                context_window=200000,
                max_tokens=4096,
                capabilities={"streaming": True, "vision": True},
            ),
            ModelInfo(
                name="claude-3-haiku-20240307",
                provider="anthropic",
                aliases=["claude-3-haiku", "haiku"],
                context_window=200000,
                max_tokens=4096,
                capabilities={"streaming": True, "vision": True},
            ),
        ]

        for model in default_models:
            self.register_model(model)

    def register_model(self, model_info: ModelInfo) -> None:
        self._models[model_info.name] = model_info
        for alias in model_info.aliases:
            self._aliases[alias] = model_info.name

    def get_model(self, name_or_alias: str) -> Optional[ModelInfo]:
        model_name = self._aliases.get(name_or_alias, name_or_alias)
        return self._models.get(model_name)

    def get_provider_for_model(self, name_or_alias: str) -> Optional[str]:
        model = self.get_model(name_or_alias)
        return model.provider if model else None

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        if provider:
            return [
                name
                for name, model in self._models.items()
                if model.provider == provider
            ]
        return list(self._models.keys())

    def get_model_capabilities(self, name_or_alias: str) -> Dict[str, bool]:
        model = self.get_model(name_or_alias)
        return model.capabilities if model else {}

    def validate_model_request(
        self, model_name: str, request_params: Dict[str, Any]
    ) -> Optional[str]:
        model = self.get_model(model_name)
        if not model:
            return f"Model {model_name} not found"

        max_tokens_requested = request_params.get("max_tokens")
        if max_tokens_requested and model.max_tokens:
            if max_tokens_requested > model.max_tokens:
                return f"Max tokens {max_tokens_requested} exceeds model limit {model.max_tokens}"  # noqa: E501

        return None

    def clear(self) -> None:
        self._models.clear()
        self._aliases.clear()
        self._initialize_default_models()
