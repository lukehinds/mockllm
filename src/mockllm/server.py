import importlib
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pythonjsonlogger.json import JsonFormatter

from .config import ResponseConfig
from .model_registry import ModelRegistry
from .models import AnthropicChatRequest, OpenAIChatRequest
from .registry import ProviderRegistry

log_handler = logging.StreamHandler()
log_handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    global response_config
    response_config = ResponseConfig()
    load_providers()
    setup_dynamic_routes()
    logger.info("Server initialized with dynamic routing")
    yield
    # Shutdown
    logger.info("Server shutting down")


response_config = None
model_registry = ModelRegistry()
provider_registry = ProviderRegistry()

app = FastAPI(title="Mock LLM Server", lifespan=lifespan)


def load_providers() -> None:
    """Load and register all providers."""
    # Import providers to trigger their registration
    importlib.import_module(".providers.openai", package="mockllm")
    importlib.import_module(".providers.anthropic", package="mockllm")
    logger.info(f"Loaded providers: {provider_registry.list_providers()}")


def setup_dynamic_routes() -> None:
    """Set up dynamic routes based on registered providers."""
    endpoints = provider_registry.get_all_endpoints()

    for path, providers in endpoints.items():
        if len(providers) == 1:
            # Single provider for this endpoint
            provider_info = providers[0]
            create_route(path, provider_info)
        else:
            # Multiple providers - create a router
            create_route_with_routing(path, providers)


def create_route(path: str, provider_info: Dict[str, Any]) -> None:
    """Create a route for a single provider."""
    provider_name = provider_info["provider"]
    handler_name = provider_info.get("handler", "handle_chat_completion")

    async def route_handler(
        request: Request,
    ) -> Union[Dict[str, Any], StreamingResponse]:
        global response_config
        provider = provider_registry.get_provider(provider_name, response_config)
        if not provider:
            raise HTTPException(
                status_code=500, detail=f"Provider {provider_name} not found"
            )

        # Parse request body
        body = await request.json()

        # Determine request type based on endpoint
        typed_request: Union[OpenAIChatRequest, AnthropicChatRequest, Any]
        if "chat/completions" in path:
            typed_request = OpenAIChatRequest(**body)
        elif "messages" in path:
            typed_request = AnthropicChatRequest(**body)
        else:
            typed_request = body

        handler = getattr(provider, handler_name)
        result: Union[Dict[str, Any], StreamingResponse] = await handler(typed_request)
        return result

    # Add route to FastAPI app
    app.add_api_route(
        path,
        route_handler,
        methods=[provider_info.get("method", "POST")],
        response_model=None,
    )


def create_route_with_routing(path: str, providers: list) -> None:
    """Create a route that can handle multiple providers."""

    async def route_handler(
        request: Request,
    ) -> Union[Dict[str, Any], StreamingResponse]:
        global response_config
        body = await request.json()
        model_name = body.get("model")

        # Determine provider based on model
        provider_name = model_registry.get_provider_for_model(model_name)
        if not provider_name:
            # Default to first provider
            provider_name = providers[0]["provider"]

        provider = provider_registry.get_provider(provider_name, response_config)
        if not provider:
            raise HTTPException(
                status_code=500, detail=f"Provider {provider_name} not found"
            )

        # Parse request based on provider type
        typed_request: Union[OpenAIChatRequest, AnthropicChatRequest, Any]
        if provider_name == "openai":
            typed_request = OpenAIChatRequest(**body)
        elif provider_name == "anthropic":
            typed_request = AnthropicChatRequest(**body)
        else:
            typed_request = body

        return await provider.handle_chat_completion(typed_request)

    app.add_api_route(
        path,
        route_handler,
        methods=["POST"],
        response_model=None,
    )


# Routes are now initialized in the lifespan handler


@app.get("/providers")
async def list_providers() -> Dict[str, Any]:
    """List all registered providers and their metadata."""
    providers = {}
    for name in provider_registry.list_providers():
        metadata = provider_registry.get_metadata(name)
        if metadata:
            providers[name] = {
                "version": metadata.version,
                "description": metadata.description,
                "endpoints": metadata.endpoints,
                "models": metadata.supported_models,
                "capabilities": metadata.capabilities,
            }
    return providers


@app.get("/models")
async def list_models() -> Dict[str, Any]:
    """List all supported models."""
    return {
        "models": model_registry.list_models(),
        "by_provider": {
            provider: model_registry.list_models(provider)
            for provider in provider_registry.list_providers()
        },
    }
