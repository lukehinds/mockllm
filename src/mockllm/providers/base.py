from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from fastapi.responses import StreamingResponse

from ..config import ResponseConfig


class LLMProvider(ABC):
    def __init__(self, config: ResponseConfig):
        self.config = config

    @abstractmethod
    async def handle_chat_completion(
        self, request: Any
    ) -> Union[Dict[str, Any], StreamingResponse]:
        pass

    @abstractmethod
    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        yield ""  # pragma: no cover

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.__class__.__name__,
            "version": "1.0.0",
            "capabilities": self.get_capabilities(),
            "supported_models": self.get_supported_models(),
        }

    def get_capabilities(self) -> Dict[str, bool]:
        return {
            "streaming": True,
            "function_calling": False,
            "vision": False,
            "embeddings": False,
        }

    def get_supported_models(self) -> List[str]:
        return []

    def get_endpoints(self) -> List[Dict[str, Any]]:
        return []

    def validate_request(self, request: Any) -> Optional[str]:
        return None

    def get_response_for_prompt(self, prompt: str) -> str:
        return self.config.get_response(prompt)
