import asyncio
import json
import random
from typing import Any, AsyncGenerator, Dict

import tiktoken


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())


async def apply_lag(lag_factor: int = 10) -> None:
    base_delay = 1.0 / lag_factor
    delay_with_jitter = base_delay * (0.8 + 0.4 * random.random())
    await asyncio.sleep(delay_with_jitter)


async def stream_with_lag(
    content: str, lag_enabled: bool = True, lag_factor: int = 10
) -> AsyncGenerator[str, None]:
    for char in content:
        yield char
        if lag_enabled:
            await apply_lag(lag_factor)


def extract_prompt_from_messages(messages: list) -> str:
    if not messages:
        return ""

    user_messages = []
    for message in messages:
        if hasattr(message, "role") and hasattr(message, "content"):
            if message.role == "user":
                user_messages.append(message.content)
        elif isinstance(message, dict):
            if message.get("role") == "user":
                user_messages.append(message.get("content", ""))

    return user_messages[-1] if user_messages else ""


def format_sse_message(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data)}\n\n"


def calculate_usage(
    prompt: str, response: str, model: str = "gpt-3.5-turbo"
) -> Dict[str, int]:
    prompt_tokens = count_tokens(prompt, model)
    completion_tokens = count_tokens(response, model)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
