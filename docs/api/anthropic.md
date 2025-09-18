# Anthropic Compatible API

MockLLM provides compatibility with Anthropic's Messages API.

## Endpoint

`POST /v1/messages`

## Example Request

```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Supported Features

- Message completions
- Streaming responses
- Claude model family
- Vision capabilities (simulated)
