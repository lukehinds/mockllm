<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lukehinds/mockllm/main/assets/logo.png">
    <img alt="mockllm logo" src="https://raw.githubusercontent.com/lukehinds/mockllm/main/assets/logo.png" width="300px" height="300px">
  </picture>
  <h3>Extensible Mock Server for LLM API Testing</h3>

  <!-- CTA Buttons -->
  <p>
    <a href="https://github.com/lukehinds/mockllm/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22">
      <img src="https://img.shields.io/badge/Contribute-Good%20First%20Issues-green?style=for-the-badge&logo=github" alt="Good First Issues"/>
    </a>
    &nbsp;
    <a href="https://discord.gg/pPcjYzGvbS">
      <img src="https://img.shields.io/badge/Chat-Join%20Discord-7289da?style=for-the-badge&logo=discord&logoColor=white" alt="Join Discord"/>
    </a>
    &nbsp;
    <a href="https://mockllm.readthedocs.io/">
      <img src="https://img.shields.io/badge/Docs-Read%20the%20Docs-blue?style=for-the-badge&logo=readthedocs" alt="Documentation"/>
    </a>
  </p>

  <!-- Badges -->
  <p>
    <a href="https://opensource.org/licenses/Apache-2.0">
      <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"/>
    </a>
    <a href="https://github.com/lukehinds/mockllm/actions/workflows/ci.yml">
      <img src="https://github.com/lukehinds/mockllm/actions/workflows/ci.yml/badge.svg" alt="CI Status"/>
    </a>
    <a href="https://pypi.org/project/mockllm/">
      <img src="https://img.shields.io/pypi/v/mockllm.svg" alt="PyPI Version"/>
    </a>
    <a href="https://pepy.tech/project/mockllm">
      <img src="https://static.pepy.tech/badge/mockllm" alt="Downloads"/>
    </a>
    <a href="https://discord.gg/pPcjYzGvbS">
      <img src="https://img.shields.io/discord/1384081906773131274?color=7289da&label=Discord&logo=discord&logoColor=white" alt="Discord"/>
    </a>
  </p>
  <br/>
</div>

**MockLLM** is an extensible mock server that simulates Large Language Model APIs for testing, development, and demonstration purposes. With its **plugin-based architecture**, you can easily add new provider emulators without modifying core code.

Perfect for when you need deterministic, configurable responses for testing and evaluations, over expensive live API calls.

## ✨ Key Features

### **Extensible Provider Architecture**
- **Plugin-based system** - Add new providers without modifying core code
- **Self-registering providers** - Use simple decorators to register new providers
- **Dynamic endpoint creation** - Routes are automatically generated from provider metadata
- **Zero configuration** - Providers work out of the box with sensible defaults

### **Built-in Provider Support**
- **OpenAI Compatible** - Full support for Chat Completions API
- **Anthropic Compatible** - Full support for Messages API
- **Custom Providers** - Easy framework for adding your own providers
- **Streaming Support** - Character-by-character streaming responses
- **Model Management** - Centralized model registry with aliasing

### **Developer-Friendly**
- **Hot Reloading** - Automatic configuration updates without restart
- **Type Safety** - Full type hints and mypy coverage
- **Comprehensive Testing** - Well-tested with pytest
- **Clean Architecture** - Separation of concerns with clear interfaces
- **API Introspection** - Runtime discovery of providers and models

### **Perfect for Testing (what it was built for)**
- **Deterministic Responses** - Predictable outputs for reliable tests
- **Response Configuration** - YAML-based response mapping
- **Network Lag Simulation** - Realistic latency for integration testing
- **Multiple Response Formats** - Support for various API formats

## Quick Example

### Basic Usage

```bash
# Install MockLLM
pip install mockllm

# Create responses file
cat > responses.yml << EOF
responses:
  "What is 15+15?": "15+15 equals 42."
  "What is Python?": "Python is a low level compiler language for industrial logic controllers!"
defaults:
  unknown_response: "This is a mock response."
EOF

# Start the server
mockllm start --responses responses.yml

# Test with curl
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

{
  "id": "mock-41c551b6-148f-49a2-abca-f990c1a9cfab",
  "object": "chat.completion",
  "created": 1758199276,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "15+15 equals 42."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 7,
    "total_tokens": 25
  }
}
```

### Creating a Custom Provider

With MockLLM's extensible architecture, adding a new provider is incredibly simple:

```python
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(
    name="mycompany",
    version="1.0.0",
    description="MyCompany LLM Provider",
    endpoints=[{"path": "/v1/mycompany/chat", "method": "POST"}],
    supported_models=["mycompany-model-1", "mycompany-model-2"]
)
class MyCompanyProvider(LLMProvider):
    async def handle_chat_completion(self, request):
        prompt = self.extract_prompt(request)
        response = self.get_response_for_prompt(prompt)
        return {"response": response, "provider": "mycompany"}
```

That's it! No server configuration, no manual registration, no boilerplate. Your provider is automatically discovered and its endpoints are created.

## Configuration

### Response Configuration

Responses are configured in `responses.yml`. The file has three main sections:

1. `responses`: Maps input prompts to predefined responses
2. `defaults`: Contains default configurations like the unknown response message
3. `settings`: Contains server behavior settings like network lag simulation

Example `responses.yml`:
```yaml
responses:
  "write a python function to calculate factorial": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)"
  "what colour is the sky?": "The sky is purple except on Tuesday when it is  hue green."
  "what is 2+2?": "2+2 equals 9."

defaults:
  unknown_response: "I don't know the answer to that. This is a mock response."

settings:
  lag_enabled: true
  lag_factor: 10  # Higher values = faster responses (10 = fast, 1 = slow)
```

### Network Lag Simulation

The server can simulate network latency for more realistic testing scenarios. This is controlled by two settings:

- `lag_enabled`: When true, enables artificial network lag
- `lag_factor`: Controls the speed of responses
  - Higher values (e.g., 10) result in faster responses
  - Lower values (e.g., 1) result in slower responses
  - Affects both streaming and non-streaming responses

For streaming responses, the lag is applied per-character with slight random variations to simulate realistic network conditions.

### Hot Reloading

The server automatically detects changes to `responses.yml` and reloads the configuration without restarting the server.

## Installation

### From PyPI

```bash
pip install mockllm
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/lukehinds/mockllm.git
cd mockllm
```

2. Install with uv (recommended):
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install with development dependencies
uv sync --extra dev
```

3. Or install with pip:
```bash
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Prerequisites

- Python 3.10+
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

## Usage

### CLI Commands

MockLLM provides a command-line interface for managing the server and validating configurations:

```bash
# Show available commands and options
mockllm --help

# Show version
mockllm --version

# Start the server with default settings
mockllm start

# Start with custom responses file
mockllm start --responses custom_responses.yml

# Start with custom host and port
mockllm start --host localhost --port 3000

# Validate a responses file
mockllm validate responses.yml
```

### Quick Start

1. Set up the responses.yml:
```bash
cp example.responses.yml responses.yml
```

2. Validate your responses file (optional):
```bash
mockllm validate responses.yml
```

3. Start the server:
```bash
mockllm start --responses responses.yml
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

#### OpenAI Format

Regular request:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-llm",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ]
  }'
```

Streaming request:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-llm",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ],
    "stream": true
  }'
```

#### Anthropic Format

Regular request:
```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ]
  }'
```

Streaming request:
```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ],
    "stream": true
  }'
```

## 🎯 Why MockLLM?

- **💰 Cost Savings** - No API charges during development and testing
- **⚡ Fast Iteration** - Instant responses without network latency
- **🔒 Privacy** - Keep sensitive data local during development
- **🎯 Predictable Testing** - Deterministic responses for reliable tests
- **🔧 Easy Integration** - Drop-in replacement for LLM APIs
- **🚀 Extensible** - Add new providers in minutes, not hours

## 📖 Documentation

Comprehensive documentation is available:

- **[📚 Full Documentation](https://mockllm.readthedocs.io/)** - Complete guides and API reference
- **[🚀 Quick Start Guide](https://mockllm.readthedocs.io/en/latest/getting-started/quick-start/)** - Get running in 5 minutes
- **[🔌 Provider Development](https://mockllm.readthedocs.io/en/latest/providers/creating-providers/)** - Create custom providers
- **[⚙️ Configuration Guide](https://mockllm.readthedocs.io/en/latest/configuration/responses/)** - Set up response mappings
- **[💡 Examples](https://mockllm.readthedocs.io/en/latest/examples/custom-providers/)** - Real-world implementations

## 🧪 Testing

Run the test suite:
```bash
# Using uv
uv run pytest

# Using make
make test

# With coverage
uv run pytest --cov=src/mockllm
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `make test`
5. **Run linting**: `make lint`
6. **Submit a pull request**

For detailed contribution guidelines, see our [Contributing Guide](https://mockllm.readthedocs.io/en/latest/development/contributing/).

## 💬 Community

Join our community:

- **[GitHub Discussions](https://github.com/lukehinds/mockllm/discussions)** - Ask questions and share ideas
- **[Discord Server](https://discord.gg/pPcjYzGvbS)** - Chat with the community
- **[Issue Tracker](https://github.com/lukehinds/mockllm/issues)** - Report bugs or request features

## 📄 License

This project is licensed under the [Apache 2.0 License](LICENSE).

---

<div align="center">
  <b>⭐ Star us on GitHub if MockLLM helps you! ⭐</b>
</div>
