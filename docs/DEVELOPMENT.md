# MockLLM Documentation

This directory contains the source files for MockLLM's documentation, built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
# Using pip
pip install -e ".[docs]"

# Using uv
uv sync --extra docs
```

### Local Development

To serve the documentation locally with live reload:

```bash
mkdocs serve
```

The documentation will be available at `http://localhost:8000/` (note: different from the MockLLM server port).

### Building Static Site

To build the static documentation site:

```bash
mkdocs build
```

The built site will be in the `site/` directory.

## Documentation Structure

```
docs/
├── index.md                    # Home page
├── getting-started/            # Installation and quick start guides
│   ├── installation.md
│   ├── quick-start.md
│   └── basic-usage.md
├── configuration/              # Configuration guides
│   ├── responses.md
│   ├── settings.md
│   └── environment.md
├── providers/                  # Provider development documentation
│   ├── architecture.md        # System architecture overview
│   ├── creating-providers.md   # How to create custom providers
│   ├── registry.md            # Provider registry details
│   ├── models.md              # Model registry system
│   └── built-in.md           # Built-in provider reference
├── api/                       # API reference documentation
│   ├── endpoints.md
│   ├── openai.md
│   ├── anthropic.md
│   └── custom.md
├── examples/                  # Example code and tutorials
│   ├── testing.md
│   ├── custom-providers.md
│   └── integrations.md
├── development/               # Development guides
│   ├── contributing.md
│   ├── testing.md
│   └── code-style.md
├── cli.md                     # CLI reference
└── changelog.md              # Version history
```

## Key Documentation Files

### Provider Development
The heart of MockLLM's extensibility:
- `providers/architecture.md` - Understand the plugin architecture
- `providers/creating-providers.md` - Step-by-step provider creation guide
- `examples/custom-providers.md` - Real-world provider examples

### Getting Started
For new users:
- `getting-started/quick-start.md` - Get running in 5 minutes
- `getting-started/installation.md` - Detailed installation instructions
- `cli.md` - Complete CLI reference

### Configuration
For customization:
- `configuration/responses.md` - Response mapping configuration
- `configuration/settings.md` - Server settings

## Writing Documentation

### Style Guide

1. **Use clear headings** - Organize content with descriptive headers
2. **Include examples** - Every feature should have a code example
3. **Add diagrams** - Use Mermaid for architecture diagrams
4. **Keep it concise** - Get to the point quickly
5. **Test code examples** - Ensure all code snippets work

### Mermaid Diagrams

The documentation supports Mermaid diagrams:

```markdown
\```mermaid
graph LR
    A[Client] --> B[MockLLM]
    B --> C[Provider]
    C --> D[Response]
\```
```

### Code Highlighting

Use language identifiers for syntax highlighting:

```markdown
\```python
from mockllm.providers.base import LLMProvider
\```
```

### Admonitions

Use admonitions for important notes:

```markdown
!!! note
    This is an important note.

!!! warning
    This is a warning.

!!! tip
    This is a helpful tip.
```

## Deployment

The documentation can be deployed to:

### GitHub Pages

```yaml
# .github/workflows/docs.yml
name: Deploy Docs
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -e ".[docs]"
      - run: mkdocs gh-deploy --force
```

### Read the Docs

Configure in `.readthedocs.yml`:

```yaml
version: 2
python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
mkdocs:
  configuration: mkdocs.yml
```

### Netlify

```toml
# netlify.toml
[build]
  command = "pip install -e '.[docs]' && mkdocs build"
  publish = "site"
```

## Contributing

To contribute to the documentation:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `mkdocs serve`
5. Submit a pull request

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Documentation](https://mermaid-js.github.io/)