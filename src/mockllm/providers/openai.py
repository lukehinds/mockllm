from typing import Any, AsyncGenerator, Dict, List, Union

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ..config import ResponseConfig
from ..models import (
    OpenAIChatRequest,
    OpenAIChatResponse,
    OpenAIDeltaMessage,
    OpenAIStreamChoice,
    OpenAIStreamResponse,
)
from ..provider_utils import (
    calculate_usage,
    extract_prompt_from_messages,
)
from ..registry import register_provider
from .base import LLMProvider


@register_provider(
    name="openai",
    version="1.0.0",
    description="OpenAI Chat Completions API provider",
    endpoints=[
        {
            "path": "/v1/chat/completions",
            "method": "POST",
            "handler": "handle_chat_completion",
        }
    ],
    supported_models=[
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
    ],
    capabilities={
        "streaming": True,
        "function_calling": True,
        "vision": True,
    },
)
class OpenAIProvider(LLMProvider):
    def __init__(self, response_config: ResponseConfig):
        super().__init__(response_config)
        self.response_config = response_config

    def get_supported_models(self) -> List[str]:
        return [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
        ]

    def get_endpoints(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/v1/chat/completions",
                "method": "POST",
                "handler": "handle_chat_completion",
            }
        ]

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        first_chunk = OpenAIStreamResponse(
            model=model,
            choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(role="assistant"))],
        )
        yield f"data: {first_chunk.model_dump_json()}\n\n"

        async for chunk in self.response_config.get_streaming_response_with_lag(
            content
        ):
            chunk_response = OpenAIStreamResponse(
                model=model,
                choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(content=chunk))],
            )
            yield f"data: {chunk_response.model_dump_json()}\n\n"

        final_chunk = OpenAIStreamResponse(
            model=model,
            choices=[
                OpenAIStreamChoice(delta=OpenAIDeltaMessage(), finish_reason="stop")
            ],
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    async def handle_chat_completion(
        self, request: OpenAIChatRequest
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

        return OpenAIChatResponse(
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_content},
                    "finish_reason": "stop",
                }
            ],
            usage=usage,
        ).model_dump()
