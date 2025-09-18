# Testing with MockLLM

MockLLM is perfect for testing applications that integrate with LLM APIs. This guide shows how to use MockLLM in your test suites.

## Basic Test Setup

### pytest Example

```python
import pytest
import requests
from subprocess import Popen
import time

@pytest.fixture(scope="session")
def mockllm_server():
    # Start MockLLM server
    process = Popen(["mockllm", "start", "--responses", "test-responses.yml"])
    time.sleep(2)  # Wait for server to start

    yield "http://localhost:8000"

    # Cleanup
    process.terminate()

def test_llm_integration(mockllm_server):
    response = requests.post(
        f"{mockllm_server}/v1/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    assert response.status_code == 200
    assert "choices" in response.json()
```

## Test Configuration

Create `test-responses.yml`:

```yaml
responses:
  "test input": "expected output"
  "error case": "error response"

defaults:
  unknown_response: "default test response"
```

## Integration Examples

### OpenAI SDK Testing

```python
from openai import OpenAI

def test_with_openai_sdk():
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="test-key"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}]
    )

    assert response.choices[0].message.content == "expected output"
```

## Next Steps

- [Custom Providers](custom-providers.md)
- [Integration Examples](integrations.md)