# Creating Custom Providers

MockLLM's extensible architecture makes it incredibly easy to add new LLM providers. This guide will walk you through creating your own provider from scratch.

## Overview

Creating a provider involves:

1. **Inheriting from `LLMProvider`** - The base class provides common functionality
2. **Using the `@register_provider` decorator** - Automatically registers your provider
3. **Implementing request handlers** - Define how your provider processes requests
4. **Declaring metadata** - Specify endpoints, models, and capabilities

## Basic Provider Example

Here's a minimal provider implementation:

```python
from typing import Any, Dict, Union
from fastapi.responses import StreamingResponse

from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(
    name="simple",
    version="1.0.0",
    description="A simple example provider",
    endpoints=[{"path": "/v1/simple/chat", "method": "POST"}],
    supported_models=["simple-model"],
    capabilities={"streaming": False}
)
class SimpleProvider(LLMProvider):
    async def handle_chat_completion(self, request: Any) -> Dict[str, Any]:
        # Extract the prompt from the request
        prompt = self.get_response_for_prompt(
            request.get("prompt", "")
        )

        return {
            "response": prompt,
            "model": request.get("model", "simple-model"),
            "provider": "simple"
        }
```

That's it! Your provider is now available at `http://localhost:8000/v1/simple/chat`.

## Full-Featured Provider Example

Here's a more complete example with streaming, multiple endpoints, and proper request handling:

```python
from typing import Any, AsyncGenerator, Dict, List, Union
from fastapi.responses import StreamingResponse

from mockllm.providers.base import LLMProvider
from mockllm.provider_utils import (
    calculate_usage,
    extract_prompt_from_messages,
    stream_with_lag
)
from mockllm.registry import register_provider

@register_provider(
    name="mycompany",
    version="2.0.0",
    description="MyCompany LLM API Provider",
    endpoints=[
        {"path": "/v1/mycompany/chat", "method": "POST"},
        {"path": "/v1/mycompany/complete", "method": "POST"},
        {"path": "/v1/mycompany/embeddings", "method": "POST"}
    ],
    supported_models=[
        "mycompany-small",
        "mycompany-large",
        "mycompany-turbo"
    ],
    capabilities={
        "streaming": True,
        "function_calling": True,
        "vision": False,
        "embeddings": True
    }
)
class MyCompanyProvider(LLMProvider):

    def get_supported_models(self) -> List[str]:
        """Return list of supported models."""
        return [
            "mycompany-small",
            "mycompany-large",
            "mycompany-turbo"
        ]

    def get_capabilities(self) -> Dict[str, bool]:
        """Return provider capabilities."""
        return {
            "streaming": True,
            "function_calling": True,
            "vision": False,
            "embeddings": True
        }

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response in custom format."""
        # Start of stream
        yield '{"type": "start", "model": "' + model + '"}\n'

        # Stream content character by character
        async for char in stream_with_lag(
            content,
            self.config.settings.get("lag_enabled", True),
            self.config.settings.get("lag_factor", 10)
        ):
            yield '{"type": "delta", "content": "' + char + '"}\n'

        # End of stream
        yield '{"type": "end", "finish_reason": "stop"}\n'

    async def handle_chat_completion(
        self, request: Dict[str, Any]
    ) -> Union[Dict[str, Any], StreamingResponse]:
        """Handle chat completion requests."""
        # Extract prompt from messages
        messages = request.get("messages", [])
        prompt = extract_prompt_from_messages(messages)

        # Validate request
        error = self.validate_request(request)
        if error:
            return {"error": error, "status": 400}

        # Get response from configuration
        response_content = self.get_response_for_prompt(prompt)

        # Handle streaming
        if request.get("stream", False):
            return StreamingResponse(
                self.generate_stream_response(
                    response_content,
                    request.get("model", "mycompany-small")
                ),
                media_type="application/x-ndjson"
            )

        # Calculate token usage
        usage = calculate_usage(
            str(messages),
            response_content,
            request.get("model", "mycompany-small")
        )

        # Return non-streaming response
        return {
            "id": f"mycompany-{self._generate_id()}",
            "object": "chat.completion",
            "created": self._timestamp(),
            "model": request.get("model", "mycompany-small"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": usage,
            "provider": "mycompany"
        }

    async def handle_completion(
        self, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle text completion requests."""
        prompt = request.get("prompt", "")
        response = self.get_response_for_prompt(prompt)

        return {
            "id": f"mycompany-{self._generate_id()}",
            "object": "text.completion",
            "created": self._timestamp(),
            "model": request.get("model", "mycompany-small"),
            "choices": [{
                "text": response,
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": calculate_usage(prompt, response)
        }

    async def handle_embeddings(
        self, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle embedding requests."""
        input_text = request.get("input", "")

        # Generate mock embeddings (random for demo)
        import random
        embedding = [random.random() for _ in range(768)]

        return {
            "object": "list",
            "data": [{
                "object": "embedding",
                "embedding": embedding,
                "index": 0
            }],
            "model": request.get("model", "mycompany-small"),
            "usage": {
                "prompt_tokens": len(input_text.split()),
                "total_tokens": len(input_text.split())
            }
        }

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _timestamp(self) -> int:
        """Get current timestamp."""
        import time
        return int(time.time())
```

## Provider Registration Deep Dive

The `@register_provider` decorator accepts these parameters:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | `str` | Unique identifier for the provider | Yes |
| `version` | `str` | Provider version (semantic versioning) | No |
| `description` | `str` | Human-readable description | No |
| `endpoints` | `List[Dict]` | API endpoints this provider handles | Yes |
| `supported_models` | `List[str]` | Model names this provider supports | No |
| `capabilities` | `Dict[str, Any]` | Provider capabilities and features | No |
| `config_schema` | `Dict` | JSON schema for provider-specific config | No |

### Endpoint Configuration

Each endpoint in the `endpoints` list should specify:

```python
{
    "path": "/v1/custom/chat",      # API path
    "method": "POST",                # HTTP method
    "handler": "handle_chat_completion"  # Method name to call
}
```

## Inheriting from LLMProvider

The `LLMProvider` base class provides several useful methods:

### Available Methods

```python
class MyProvider(LLMProvider):
    # Required to implement
    async def handle_chat_completion(self, request: Any) -> Union[Dict, StreamingResponse]:
        pass

    # Optional to override
    def get_supported_models(self) -> List[str]:
        return ["model-1", "model-2"]

    def get_capabilities(self) -> Dict[str, bool]:
        return {"streaming": True}

    def validate_request(self, request: Any) -> Optional[str]:
        # Return error message if invalid, None if valid
        if not request.get("model"):
            return "Model is required"
        return None

    # Utility methods available
    def get_response_for_prompt(self, prompt: str) -> str:
        # Gets response from YAML configuration
        return super().get_response_for_prompt(prompt)
```

## Advanced Features

### Custom Request/Response Models

Use Pydantic models for type safety:

```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    prompt: str
    model: str = "mycompany-small"
    temperature: float = 1.0
    max_tokens: int = 100

class MyResponse(BaseModel):
    id: str
    response: str
    tokens_used: int

class MyProvider(LLMProvider):
    async def handle_chat_completion(
        self, request: MyRequest
    ) -> MyResponse:
        response = self.get_response_for_prompt(request.prompt)
        return MyResponse(
            id=self._generate_id(),
            response=response,
            tokens_used=len(response.split())
        )
```

### Provider-Specific Configuration

Add custom configuration options:

```python
@register_provider(
    name="custom",
    config_schema={
        "type": "object",
        "properties": {
            "api_version": {"type": "string"},
            "custom_setting": {"type": "boolean"}
        }
    }
)
class CustomProvider(LLMProvider):
    def __init__(self, config):
        super().__init__(config)
        # Access provider-specific config
        self.api_version = config.provider_config.get(
            "api_version", "v1"
        )
```

### Multiple Handler Methods

Support different endpoints with different handlers:

```python
@register_provider(
    name="multi",
    endpoints=[
        {"path": "/v1/multi/chat", "handler": "handle_chat"},
        {"path": "/v1/multi/image", "handler": "handle_image"},
        {"path": "/v1/multi/audio", "handler": "handle_audio"}
    ]
)
class MultiProvider(LLMProvider):
    async def handle_chat(self, request):
        return {"type": "chat", "response": "..."}

    async def handle_image(self, request):
        return {"type": "image", "url": "..."}

    async def handle_audio(self, request):
        return {"type": "audio", "data": "..."}
```

## Testing Your Provider

Create a test file for your provider:

```python
import pytest
from fastapi.testclient import TestClient
from mockllm.server import app

client = TestClient(app)

def test_custom_provider():
    response = client.post(
        "/v1/custom/chat",
        json={"prompt": "Hello", "model": "custom-model"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["provider"] == "custom"

def test_custom_streaming():
    response = client.post(
        "/v1/custom/chat",
        json={"prompt": "Hello", "stream": true}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
```

## Best Practices

1. **Use Type Hints** - Add type annotations for better IDE support
2. **Validate Requests** - Always validate incoming requests
3. **Handle Errors Gracefully** - Return meaningful error messages
4. **Document Your Provider** - Add docstrings and comments
5. **Follow Conventions** - Use consistent naming and structure
6. **Test Thoroughly** - Write tests for all endpoints and edge cases
7. **Use Utilities** - Leverage the provided utility functions

## Loading External Providers

Providers can be loaded from external packages:

```python
# In your external package: my_provider.py
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(name="external", ...)
class ExternalProvider(LLMProvider):
    pass

# In your server startup
import importlib

def load_external_providers():
    # Load provider from external package
    importlib.import_module("my_company.providers.my_provider")
```

## Next Steps

- See [Provider Registry](registry.md) for advanced registry features
- Check [Built-in Providers](built-in.md) for implementation examples
- Read [Architecture Overview](architecture.md) to understand the system design
- Explore [Examples](../examples/custom-providers.md) for more provider implementations