"""
Example custom provider to demonstrate extensibility.

This provider shows how to create a new LLM provider that:
1. Self-registers using the @register_provider decorator
2. Supports custom models and endpoints
3. Can be loaded dynamically without modifying core code
"""

from typing import Any, AsyncGenerator, Dict, List, Union

from fastapi.responses import StreamingResponse

from ..config import ResponseConfig
from ..provider_utils import calculate_usage, extract_prompt_from_messages
from ..registry import register_provider
from .base import LLMProvider


@register_provider(
    name="custom",
    version="1.0.0",
    description="Custom example LLM provider",
    endpoints=[
        {
            "path": "/v1/custom/chat",
            "method": "POST",
            "handler": "handle_chat_completion",
        },
        {
            "path": "/v1/custom/complete",
            "method": "POST",
            "handler": "handle_completion",
        },
    ],
    supported_models=[
        "custom-base",
        "custom-large",
        "custom-turbo",
    ],
    capabilities={
        "streaming": True,
        "function_calling": False,
        "vision": False,
        "embeddings": True,
    },
)
class CustomProvider(LLMProvider):
    """Example custom provider implementation."""

    def __init__(self, response_config: ResponseConfig):
        super().__init__(response_config)
        self.response_config = response_config

    def get_supported_models(self) -> List[str]:
        return ["custom-base", "custom-large", "custom-turbo"]

    def get_endpoints(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/v1/custom/chat",
                "method": "POST",
                "handler": "handle_chat_completion",
            },
            {
                "path": "/v1/custom/complete",
                "method": "POST",
                "handler": "handle_completion",
            },
        ]

    def get_capabilities(self) -> Dict[str, bool]:
        return {
            "streaming": True,
            "function_calling": False,
            "vision": False,
            "embeddings": True,
        }

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate custom streaming response format."""
        # Custom format: JSON lines with type and content
        yield f'{{"type": "start", "model": "{model}"}}\n'

        async for chunk in self.response_config.get_streaming_response_with_lag(
            content
        ):
            yield f'{{"type": "chunk", "content": "{chunk}"}}\n'

        yield '{"type": "end", "finish_reason": "stop"}\n'

    async def handle_chat_completion(
        self, request: Any
    ) -> Union[Dict[str, Any], StreamingResponse]:
        """Handle custom chat completion requests."""
        # Extract prompt from request
        messages = request.get("messages", [])
        prompt = extract_prompt_from_messages(messages)

        if not prompt and messages:
            # Fallback to last message
            last_msg = messages[-1]
            prompt = last_msg.get("content", "")

        # Get response from configuration
        response_content = self.get_response_for_prompt(prompt)

        # Handle streaming
        stream = request.get("stream", False)
        if stream:
            return StreamingResponse(
                self.generate_stream_response(
                    response_content, request.get("model", "custom-base")
                ),
                media_type="application/x-ndjson",
            )

        # Non-streaming response
        usage = calculate_usage(
            str(messages), response_content, request.get("model", "custom-base")
        )

        return {
            "id": "custom-response-001",
            "object": "chat.completion",
            "model": request.get("model", "custom-base"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": usage,
            "custom_metadata": {
                "provider": "custom",
                "version": "1.0.0",
            },
        }

    async def handle_completion(self, request: Any) -> Dict[str, Any]:
        """Handle simple text completion requests."""
        prompt = request.get("prompt", "")
        response_content = self.get_response_for_prompt(prompt)

        usage = calculate_usage(
            prompt, response_content, request.get("model", "custom-base")
        )

        return {
            "id": "custom-completion-001",
            "object": "text.completion",
            "model": request.get("model", "custom-base"),
            "choices": [
                {
                    "text": response_content,
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": usage,
        }
