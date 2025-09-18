# API Endpoints

MockLLM provides multiple API endpoints that mimic popular LLM services.

## Built-in Endpoints

### OpenAI Compatible

- `POST /v1/chat/completions` - Chat completions
- `GET /providers` - List available providers
- `GET /models` - List supported models

### Anthropic Compatible

- `POST /v1/messages` - Message completions

## Custom Endpoints

Providers can define custom endpoints:

```python
@register_provider(
    endpoints=[
        {"path": "/v1/custom/endpoint", "method": "POST"}
    ]
)
class CustomProvider(LLMProvider):
    pass
```

## Response Format

All endpoints return JSON responses with appropriate status codes:

- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

## Next Steps

- [OpenAI API](openai.md)
- [Anthropic API](anthropic.md)
- [Custom APIs](custom.md)