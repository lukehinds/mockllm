from typing import Any, AsyncGenerator, Dict, List, Union

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ..config import ResponseConfig
from ..models import (
    AnthropicChatRequest,
    AnthropicChatResponse,
    AnthropicStreamDelta,
    AnthropicStreamResponse,
)
from ..provider_utils import calculate_usage, extract_prompt_from_messages
from ..registry import register_provider
from .base import LLMProvider


@register_provider(
    name="anthropic",
    version="1.0.0",
    description="Anthropic Messages API provider",
    endpoints=[
        {
            "path": "/v1/messages",
            "method": "POST",
            "handler": "handle_chat_completion",
        }
    ],
    supported_models=[
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
    ],
    capabilities={
        "streaming": True,
        "vision": True,
        "function_calling": False,
    },
)
class AnthropicProvider(LLMProvider):
    def __init__(self, response_config: ResponseConfig):
        super().__init__(response_config)
        self.response_config = response_config

    def get_supported_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]

    def get_endpoints(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/v1/messages",
                "method": "POST",
                "handler": "handle_chat_completion",
            }
        ]

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.response_config.get_streaming_response_with_lag(
            content
        ):
            stream_response = AnthropicStreamResponse(
                delta=AnthropicStreamDelta(delta={"text": chunk})
            )
            yield f"data: {stream_response.model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    async def handle_chat_completion(
        self, request: AnthropicChatRequest
    ) -> Union[Dict[str, Any], StreamingResponse]:
        prompt = extract_prompt_from_messages(request.messages)

        if not prompt:
            last_message = next(
                (msg for msg in reversed(request.messages) if msg.role == "user"), None
            )
            if last_message:
                prompt = last_message.content
            else:
                raise HTTPException(
                    status_code=400, detail="No user message found in request"
                )

        if request.stream:
            response_content = self.get_response_for_prompt(prompt)
            return StreamingResponse(
                self.generate_stream_response(response_content, request.model),
                media_type="text/event-stream",
            )

        response_content = await self.response_config.get_response_with_lag(prompt)

        usage = calculate_usage(str(request.messages), response_content, request.model)

        return AnthropicChatResponse(
            model=request.model,
            content=[{"type": "text", "text": response_content}],
            usage={
                "input_tokens": usage["prompt_tokens"],
                "output_tokens": usage["completion_tokens"],
                "total_tokens": usage["total_tokens"],
            },
        ).model_dump()
