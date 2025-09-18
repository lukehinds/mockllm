# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Development Setup
```bash
# Install development dependencies
make setup
# Or directly with uv
uv sync --extra dev
```

### Running Tests
```bash
# Run all tests
make test
# Run specific test file
uv run pytest tests/test_server.py -v
# Run with coverage (if needed)
uv run pytest tests/ -v --cov=src/mockllm
```

### Code Quality Checks
```bash
# Run all linting and formatting checks
make lint

# Format code (modifies files)
make format

# Individual checks:
uv run black --check .      # Check formatting
uv run isort --check .      # Check import sorting
uv run ruff check .         # Run linter
uv run mypy src/            # Type checking
```

### Building and Running
```bash
# Run the server locally
make run
# Or with custom responses file
mockllm start --responses custom_responses.yml

# Build package
make build

# Validate responses file
mockllm validate responses.yml
```

## Architecture Overview

MockLLM uses a **plugin-based provider architecture** that makes it extremely easy to add new LLM providers without modifying core code. The system automatically discovers and registers providers at startup.

### Core Components

1. **Provider Registry System** (`src/mockllm/registry.py`)
   - **`ProviderRegistry`**: Singleton registry for provider discovery and management
   - **`@register_provider`**: Decorator for automatic provider registration
   - **`ProviderMetadata`**: Defines provider capabilities, endpoints, and models
   - Supports dynamic endpoint registration and routing

2. **Enhanced Provider Base** (`src/mockllm/providers/base.py`)
   - **`LLMProvider`**: Enhanced abstract base class with metadata support
   - Common utilities for token counting, response formatting, and error handling
   - Support for provider capabilities (streaming, function calling, vision, etc.)
   - Automatic prompt extraction and response handling

3. **Model Registry** (`src/mockllm/model_registry.py`)
   - **`ModelRegistry`**: Centralized model management and validation
   - **`ModelInfo`**: Model metadata including capabilities and limits
   - Model aliasing and provider routing based on model names
   - Automatic validation of model requests and parameters

4. **Provider Utilities** (`src/mockllm/provider_utils.py`)
   - Shared utilities for common provider tasks
   - Token counting, lag simulation, and response formatting
   - Message extraction and usage calculation helpers

5. **Dynamic Server** (`src/mockllm/server.py`)
   - **Dynamic endpoint registration**: Routes created automatically from provider metadata
   - **Provider routing**: Automatic provider selection based on model or endpoint
   - **Lifespan management**: Provider initialization on startup
   - **API introspection**: `/providers` and `/models` endpoints for discovery

### Adding New Providers

Adding a new provider requires only creating a new file with the `@register_provider` decorator:

```python
@register_provider(
    name="custom",
    version="1.0.0",
    description="My custom LLM provider",
    endpoints=[{"path": "/v1/custom/chat", "method": "POST"}],
    supported_models=["custom-model-1", "custom-model-2"],
    capabilities={"streaming": True, "function_calling": False}
)
class CustomProvider(LLMProvider):
    # Implementation here
```

### Key Workflows

1. **Provider Registration**:
   - Providers self-register using decorators
   - Metadata is collected during import
   - Routes are dynamically created at startup

2. **Request Routing**:
   - Model-based routing for overlapping endpoints
   - Automatic request type detection and parsing
   - Provider-specific error handling and validation

3. **Response Generation**:
   - Configurable lag simulation per provider
   - Streaming support with provider-specific formats
   - Automatic usage calculation and metadata injection

4. **Hot Reload**: Configuration changes are automatically detected and applied without restart

### Provider Examples

- **OpenAI Provider**: Supports Chat Completions API with streaming
- **Anthropic Provider**: Supports Messages API with vision capabilities
- **Custom Provider**: Example showing custom endpoints and response formats

## Development Notes

- **Extensible by design**: Adding new providers requires no core code changes
- **Type-safe**: Full mypy coverage with proper type annotations
- **Plugin architecture**: Providers can be loaded from external packages
- **Backward compatible**: Existing APIs continue to work unchanged
- The project uses `uv` as the package manager
- Python 3.10+ is required
- All code must pass ruff and mypy checks
- The server runs on `http://localhost:8000` by default