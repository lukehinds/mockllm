# Quick Start

Get MockLLM up and running in under 5 minutes! This guide will walk you through creating your first mock LLM server.

## Step 1: Install MockLLM

```bash
pip install mockllm
```

## Step 2: Create a Response Configuration

Create a file named `responses.yml`:

```yaml
responses:
  "Hello": "Hi there! How can I help you today?"
  "What is Python?": "Python is a high-level programming language."
  "Tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs!"

defaults:
  unknown_response: "I'm a mock LLM. This is a default response."

settings:
  lag_enabled: true
  lag_factor: 10  # Higher = faster responses
```

## Step 3: Start the Server

```bash
mockllm start --responses responses.yml
```

You should see output like:
```
Using responses file: responses.yml
Starting server on 0.0.0.0:8000
```

## Step 4: Test Your Server

Open a new terminal and test with curl:

### OpenAI-style Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Response:
```json
{
  "id": "chatcmpl-mock",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-3.5-turbo",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hi there! How can I help you today?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

### Anthropic-style Request

```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [{"role": "user", "content": "Tell me a joke"}]
  }'
```

### Streaming Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "What is Python?"}],
    "stream": true
  }'
```

The response will stream character by character!

## Step 5: Explore Available Providers and Models

MockLLM provides introspection endpoints:

### List All Providers

```bash
curl http://localhost:8000/providers
```

Response:
```json
{
  "openai": {
    "version": "1.0.0",
    "description": "OpenAI Chat Completions API provider",
    "endpoints": [
      {"path": "/v1/chat/completions", "method": "POST"}
    ],
    "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
    "capabilities": {
      "streaming": true,
      "function_calling": true,
      "vision": true
    }
  },
  "anthropic": {
    "version": "1.0.0",
    "description": "Anthropic Messages API provider",
    "endpoints": [
      {"path": "/v1/messages", "method": "POST"}
    ],
    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
    "capabilities": {
      "streaming": true,
      "vision": true
    }
  }
}
```

### List All Models

```bash
curl http://localhost:8000/models
```

## Using MockLLM with Python

### OpenAI SDK

```python
from openai import OpenAI

# Point to MockLLM server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="mock-key"  # MockLLM doesn't validate keys
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
# Output: Hi there! How can I help you today?
```

### Anthropic SDK

```python
from anthropic import Anthropic

# Point to MockLLM server
client = Anthropic(
    base_url="http://localhost:8000/v1",
    api_key="mock-key"
)

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "Tell me a joke"}]
)

print(response.content[0].text)
# Output: Why do programmers prefer dark mode? Because light attracts bugs!
```

### Streaming with Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="mock-key"
)

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What is Python?"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')
```

## Using MockLLM with JavaScript/TypeScript

```javascript
// Using fetch
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: 'Hello' }]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## Using the CLI

MockLLM provides a comprehensive CLI:

```bash
# Validate your responses file
mockllm validate responses.yml

# Start with custom settings
mockllm start --host localhost --port 3000 --responses my-responses.yml

# Start with auto-reload for development
mockllm start --reload
```

## Hot Reloading

MockLLM automatically detects changes to your `responses.yml` file:

1. Start the server
2. Edit `responses.yml` and add a new response
3. Save the file
4. The server will automatically reload the configuration
5. Test the new response immediately!

## Next Steps

Congratulations! You've successfully:
- ✅ Installed MockLLM
- ✅ Created a response configuration
- ✅ Started the mock server
- ✅ Tested with curl and SDKs
- ✅ Explored available providers

Continue learning with:

- [Basic Usage](basic-usage.md) - Common patterns and use cases
- [Configuration Guide](../configuration/responses.md) - Advanced response configuration
- [Provider Development](../providers/creating-providers.md) - Create custom providers
- [Testing Guide](../examples/testing.md) - Use MockLLM in your tests