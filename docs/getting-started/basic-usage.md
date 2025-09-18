# Basic Usage

This page covers common patterns and use cases for MockLLM.

## Starting the Server

```bash
mockllm start --responses responses.yml
```

## Making Requests

### Using curl

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}]
    }
)
print(response.json())
```

## Common Patterns

- Response configuration
- Testing integration
- Development workflows

For more detailed examples, see the [Examples](../examples/testing.md) section.