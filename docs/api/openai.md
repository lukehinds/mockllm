# OpenAI Compatible API

MockLLM provides full compatibility with OpenAI's Chat Completions API.

## Endpoint

`POST /v1/chat/completions`

## Example Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Supported Features

- Chat completions
- Streaming responses
- Multiple models
- Token usage calculation
