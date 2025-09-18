# Custom Provider Examples

This guide provides real-world examples of creating custom providers for MockLLM. Each example demonstrates different capabilities and use cases.

## Example 1: Simple Echo Provider

A minimal provider that echoes back the input with modifications.

```python
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(
    name="echo",
    version="1.0.0",
    description="Echoes input with modifications",
    endpoints=[{"path": "/v1/echo", "method": "POST"}],
    supported_models=["echo-v1"]
)
class EchoProvider(LLMProvider):
    async def handle_chat_completion(self, request):
        messages = request.get("messages", [])
        last_message = messages[-1] if messages else {}
        content = last_message.get("content", "")

        # Echo with modifications
        response = f"ECHO: {content.upper()}"

        return {
            "id": "echo-001",
            "response": response,
            "original": content,
            "length": len(content)
        }
```

## Example 2: Translation Provider

A provider that simulates translation between languages.

```python
from typing import Dict, Any
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider
from mockllm.provider_utils import extract_prompt_from_messages

@register_provider(
    name="translate",
    version="1.0.0",
    description="Mock translation service",
    endpoints=[
        {"path": "/v1/translate", "method": "POST"},
        {"path": "/v1/translate/detect", "method": "POST"}
    ],
    supported_models=["translator-v1"],
    capabilities={"languages": ["en", "es", "fr", "de", "ja"]}
)
class TranslationProvider(LLMProvider):

    # Mock translations database
    TRANSLATIONS = {
        "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "ja": "こんにちは"},
        "goodbye": {"es": "adiós", "fr": "au revoir", "de": "auf wiedersehen", "ja": "さようなら"},
        "thank you": {"es": "gracias", "fr": "merci", "de": "danke", "ja": "ありがとう"}
    }

    async def handle_chat_completion(self, request: Dict[str, Any]):
        """Handle translation requests."""
        text = extract_prompt_from_messages(request.get("messages", []))
        source_lang = request.get("source_language", "en")
        target_lang = request.get("target_language", "es")

        # Mock translation logic
        text_lower = text.lower()
        if text_lower in self.TRANSLATIONS:
            translated = self.TRANSLATIONS[text_lower].get(
                target_lang,
                f"[Translation to {target_lang} not available]"
            )
        else:
            # Fallback to mock translation
            translated = f"[{target_lang}] {text}"

        return {
            "id": "translate-001",
            "source": {
                "language": source_lang,
                "text": text
            },
            "translation": {
                "language": target_lang,
                "text": translated
            },
            "confidence": 0.95
        }

    async def handle_detect(self, request: Dict[str, Any]):
        """Detect language of input text."""
        text = request.get("text", "")

        # Mock language detection
        if any(char in text for char in "áéíóúñ"):
            detected = "es"
        elif any(char in text for char in "àèìòùç"):
            detected = "fr"
        elif any(char in text for char in "äöüß"):
            detected = "de"
        elif any(ord(char) > 0x3000 for char in text):
            detected = "ja"
        else:
            detected = "en"

        return {
            "detected_language": detected,
            "confidence": 0.89,
            "alternatives": [
                {"language": "en", "confidence": 0.1},
                {"language": "unknown", "confidence": 0.01}
            ]
        }
```

## Example 3: Code Generation Provider

A provider specialized for code generation and analysis.

```python
from typing import Any, AsyncGenerator, Dict
from fastapi.responses import StreamingResponse
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider
from mockllm.provider_utils import stream_with_lag

@register_provider(
    name="codegen",
    version="2.0.0",
    description="Code generation and analysis provider",
    endpoints=[
        {"path": "/v1/code/generate", "method": "POST"},
        {"path": "/v1/code/explain", "method": "POST"},
        {"path": "/v1/code/review", "method": "POST"}
    ],
    supported_models=["codegen-python", "codegen-javascript", "codegen-multi"],
    capabilities={
        "streaming": True,
        "languages": ["python", "javascript", "typescript", "go", "rust"],
        "features": ["generation", "explanation", "review", "refactoring"]
    }
)
class CodeGenProvider(LLMProvider):

    CODE_TEMPLATES = {
        "fibonacci": {
            "python": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
            "javascript": """function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}"""
        },
        "hello_world": {
            "python": 'print("Hello, World!")',
            "javascript": 'console.log("Hello, World!");'
        }
    }

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Stream code character by character."""
        yield '{"type": "code_start", "language": "' + model.split('-')[-1] + '"}\n'

        async for char in stream_with_lag(content, True, 15):
            # Escape special characters for JSON
            char_escaped = char.replace('"', '\\"').replace('\n', '\\n')
            yield '{"type": "delta", "content": "' + char_escaped + '"}\n'

        yield '{"type": "code_end", "status": "complete"}\n'

    async def handle_generate(self, request: Dict[str, Any]):
        """Generate code based on description."""
        description = request.get("description", "")
        language = request.get("language", "python")
        stream = request.get("stream", False)

        # Find matching template
        code = None
        for template_name, templates in self.CODE_TEMPLATES.items():
            if template_name in description.lower():
                code = templates.get(language, f"// {language} not supported")
                break

        if not code:
            code = f"# TODO: Implement {description}"

        if stream:
            return StreamingResponse(
                self.generate_stream_response(code, f"codegen-{language}"),
                media_type="application/x-ndjson"
            )

        return {
            "id": "codegen-001",
            "code": code,
            "language": language,
            "description": description,
            "tokens": len(code.split())
        }

    async def handle_explain(self, request: Dict[str, Any]):
        """Explain provided code."""
        code = request.get("code", "")
        language = request.get("language", "auto")

        # Mock code explanation
        if "fibonacci" in code.lower():
            explanation = "This is a recursive implementation of the Fibonacci sequence."
        elif "print" in code or "console.log" in code:
            explanation = "This code outputs text to the console."
        else:
            explanation = "This code performs a specific operation."

        return {
            "id": "explain-001",
            "explanation": explanation,
            "language": language,
            "complexity": "O(n)" if "for" in code else "O(1)",
            "suggestions": [
                "Consider adding error handling",
                "Add type hints for better clarity"
            ]
        }

    async def handle_review(self, request: Dict[str, Any]):
        """Review code for issues and improvements."""
        code = request.get("code", "")

        issues = []
        if "eval(" in code:
            issues.append({
                "type": "security",
                "severity": "high",
                "message": "Avoid using eval() as it can execute arbitrary code"
            })

        if not any(doc in code for doc in ['"""', "'''", "//"]):
            issues.append({
                "type": "documentation",
                "severity": "medium",
                "message": "Consider adding documentation/comments"
            })

        return {
            "id": "review-001",
            "status": "reviewed",
            "issues": issues,
            "score": 85 if not issues else 60,
            "summary": f"Found {len(issues)} issues to address"
        }

    async def handle_chat_completion(self, request: Any):
        """Route to appropriate handler based on endpoint."""
        endpoint = request.get("endpoint", "generate")

        if endpoint == "explain":
            return await self.handle_explain(request)
        elif endpoint == "review":
            return await self.handle_review(request)
        else:
            return await self.handle_generate(request)
```

## Example 4: Multi-Modal Provider

A provider that handles text, images, and audio (simulated).

```python
import base64
import json
from typing import Any, Dict, List
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(
    name="multimodal",
    version="1.0.0",
    description="Multi-modal AI provider",
    endpoints=[
        {"path": "/v1/multimodal/analyze", "method": "POST"},
        {"path": "/v1/multimodal/generate", "method": "POST"}
    ],
    supported_models=["multi-v1", "vision-v1", "audio-v1"],
    capabilities={
        "modalities": ["text", "image", "audio"],
        "vision": True,
        "audio": True,
        "generation": True
    }
)
class MultiModalProvider(LLMProvider):

    async def handle_chat_completion(self, request: Dict[str, Any]):
        """Handle multi-modal requests."""
        messages = request.get("messages", [])
        model = request.get("model", "multi-v1")

        # Detect input modalities
        modalities = self._detect_modalities(messages)

        if "image" in modalities:
            return await self._handle_image_request(messages)
        elif "audio" in modalities:
            return await self._handle_audio_request(messages)
        else:
            return await self._handle_text_request(messages)

    def _detect_modalities(self, messages: List[Dict]) -> List[str]:
        """Detect what modalities are present in the request."""
        modalities = set()

        for message in messages:
            content = message.get("content", "")

            # Check for different content types
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "image":
                        modalities.add("image")
                    elif item.get("type") == "audio":
                        modalities.add("audio")
                    else:
                        modalities.add("text")
            else:
                modalities.add("text")

        return list(modalities)

    async def _handle_image_request(self, messages: List[Dict]):
        """Handle image analysis requests."""
        # Extract image data (mock analysis)
        image_count = 0
        for message in messages:
            content = message.get("content", [])
            if isinstance(content, list):
                image_count += sum(1 for item in content if item.get("type") == "image")

        return {
            "id": "vision-001",
            "analysis": {
                "objects_detected": ["person", "car", "building"],
                "scene": "urban street",
                "text_found": ["STOP", "Main St"],
                "image_count": image_count
            },
            "description": "This appears to be an urban street scene with people and vehicles.",
            "confidence": 0.92
        }

    async def _handle_audio_request(self, messages: List[Dict]):
        """Handle audio transcription/analysis requests."""
        return {
            "id": "audio-001",
            "transcription": "Hello, this is a mock transcription of the audio.",
            "language": "en",
            "duration_seconds": 10.5,
            "speaker_count": 2,
            "sentiment": "neutral"
        }

    async def _handle_text_request(self, messages: List[Dict]):
        """Handle standard text requests."""
        last_message = messages[-1] if messages else {}
        content = last_message.get("content", "")

        return {
            "id": "text-001",
            "response": f"Processed text: {content}",
            "modality": "text",
            "tokens": len(content.split())
        }

    async def handle_generate(self, request: Dict[str, Any]):
        """Generate content based on modality."""
        modality = request.get("modality", "text")
        prompt = request.get("prompt", "")

        if modality == "image":
            # Mock image generation
            return {
                "id": "gen-image-001",
                "image": {
                    "url": "https://mock.image.url/generated.png",
                    "base64": base64.b64encode(b"mock_image_data").decode(),
                    "format": "png",
                    "size": "1024x1024"
                },
                "prompt": prompt
            }
        elif modality == "audio":
            # Mock audio generation
            return {
                "id": "gen-audio-001",
                "audio": {
                    "url": "https://mock.audio.url/generated.mp3",
                    "format": "mp3",
                    "duration": 5.0
                },
                "prompt": prompt
            }
        else:
            # Text generation
            return {
                "id": "gen-text-001",
                "text": f"Generated content for: {prompt}",
                "prompt": prompt
            }
```

## Example 5: Database Query Provider

A provider that simulates natural language to SQL conversion.

```python
from typing import Any, Dict
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(
    name="dbquery",
    version="1.0.0",
    description="Natural language to SQL provider",
    endpoints=[
        {"path": "/v1/db/query", "method": "POST"},
        {"path": "/v1/db/explain", "method": "POST"}
    ],
    supported_models=["sql-generator-v1"],
    capabilities={"databases": ["mysql", "postgresql", "sqlite"]}
)
class DatabaseQueryProvider(LLMProvider):

    QUERY_PATTERNS = {
        "select all": "SELECT * FROM {table}",
        "count": "SELECT COUNT(*) FROM {table}",
        "average": "SELECT AVG({column}) FROM {table}",
        "maximum": "SELECT MAX({column}) FROM {table}",
        "join": "SELECT * FROM {table1} JOIN {table2} ON {condition}"
    }

    async def handle_chat_completion(self, request: Dict[str, Any]):
        """Convert natural language to SQL."""
        nl_query = request.get("query", "")
        database = request.get("database", "postgresql")
        schema = request.get("schema", {})

        # Mock SQL generation
        sql = self._generate_sql(nl_query, schema)

        return {
            "id": "sql-001",
            "natural_language": nl_query,
            "sql": sql,
            "database": database,
            "explanation": self._explain_query(sql),
            "estimated_cost": self._estimate_cost(sql)
        }

    def _generate_sql(self, nl_query: str, schema: Dict) -> str:
        """Generate SQL from natural language."""
        nl_lower = nl_query.lower()

        # Simple pattern matching for demo
        if "select all users" in nl_lower:
            return "SELECT * FROM users"
        elif "count" in nl_lower and "orders" in nl_lower:
            return "SELECT COUNT(*) FROM orders"
        elif "average price" in nl_lower:
            return "SELECT AVG(price) FROM products"
        elif "join" in nl_lower:
            return "SELECT * FROM users u JOIN orders o ON u.id = o.user_id"
        else:
            return "SELECT * FROM table_name WHERE condition = 'value'"

    def _explain_query(self, sql: str) -> str:
        """Explain what the SQL query does."""
        if "COUNT(*)" in sql:
            return "This query counts the total number of records."
        elif "AVG(" in sql:
            return "This query calculates the average value."
        elif "JOIN" in sql:
            return "This query combines data from multiple tables."
        else:
            return "This query retrieves data from the database."

    def _estimate_cost(self, sql: str) -> Dict[str, Any]:
        """Estimate query cost (mock)."""
        return {
            "estimated_rows": 100 if "WHERE" in sql else 1000,
            "index_used": "WHERE" in sql,
            "performance": "fast" if "LIMIT" in sql else "moderate"
        }
```

## Using Custom Providers

### Step 1: Create Your Provider File

Save your provider code in a Python file, e.g., `my_provider.py`:

```python
# my_provider.py
from mockllm.providers.base import LLMProvider
from mockllm.registry import register_provider

@register_provider(name="myprovider", ...)
class MyProvider(LLMProvider):
    # Your implementation
```

### Step 2: Load the Provider

Option 1: Place in the providers directory:
```bash
cp my_provider.py src/mockllm/providers/
```

Option 2: Import in server initialization:
```python
# In server.py or a startup script
import my_provider  # This registers it automatically
```

Option 3: Dynamic loading:
```python
# In server configuration
import importlib

def load_custom_providers():
    providers = [
        "my_company.providers.custom_provider",
        "another_package.llm_provider"
    ]
    for provider in providers:
        importlib.import_module(provider)
```

### Step 3: Test Your Provider

```python
import requests

# Test your custom endpoint
response = requests.post(
    "http://localhost:8000/v1/myprovider/endpoint",
    json={"prompt": "test"}
)
print(response.json())
```

## Best Practices

1. **Use Type Hints**: Always add type annotations for better IDE support
2. **Handle Errors**: Return appropriate error responses
3. **Document Endpoints**: Clearly document what each endpoint does
4. **Follow Naming Conventions**: Use consistent naming patterns
5. **Validate Input**: Always validate request data
6. **Test Thoroughly**: Write comprehensive tests for your provider

## Next Steps

- [Architecture Overview](../providers/architecture.md) - Understand the system design
- [Provider Registry](../providers/registry.md) - Learn about the registry system
- [Testing Guide](testing.md) - Test your providers
- [API Reference](../api/custom.md) - Document your APIs