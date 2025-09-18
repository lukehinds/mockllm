# Installation

MockLLM can be installed using pip or from source. Choose the method that best fits your needs.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Optional: [uv](https://github.com/astral-sh/uv) for faster dependency management

## Install from PyPI

The simplest way to install MockLLM is from PyPI:

```bash
pip install mockllm
```

### Install with Development Dependencies

If you plan to contribute or modify MockLLM:

```bash
pip install mockllm[dev]
```

## Install from Source

For the latest features or development work, install directly from the repository:

### Using pip

```bash
# Clone the repository
git clone https://github.com/lukehinds/mockllm.git
cd mockllm

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that MockLLM uses for development:

```bash
# Clone the repository
git clone https://github.com/lukehinds/mockllm.git
cd mockllm

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install with development dependencies
uv sync --extra dev
```

## Docker Installation

You can also run MockLLM using Docker:

```bash
# Pull the image (when available)
docker pull mockllm/mockllm:latest

# Or build from source
git clone https://github.com/lukehinds/mockllm.git
cd mockllm
docker build -t mockllm .

# Run the container
docker run -p 8000:8000 -v $(pwd)/responses.yml:/app/responses.yml mockllm
```

## Verify Installation

After installation, verify that MockLLM is properly installed:

```bash
# Check the version
mockllm --version

# View available commands
mockllm --help

# Validate installation by starting the server
mockllm start --help
```

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.10+
- **RAM**: 256MB
- **Disk**: 50MB

### Recommended Requirements
- **OS**: Linux or macOS
- **Python**: 3.11+
- **RAM**: 512MB
- **Disk**: 100MB

## Troubleshooting Installation

### Common Issues

#### Permission Denied Error
If you encounter permission errors during installation:

```bash
# Use user installation
pip install --user mockllm

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mockllm
```

#### SSL Certificate Errors
If you encounter SSL errors:

```bash
# Upgrade pip and certificates
pip install --upgrade pip certifi

# Or use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org mockllm
```

#### Dependency Conflicts
If you have dependency conflicts:

```bash
# Create a clean virtual environment
python -m venv mockllm-env
source mockllm-env/bin/activate
pip install mockllm
```

## Platform-Specific Notes

### macOS
- Ensure you have Xcode Command Line Tools installed:
  ```bash
  xcode-select --install
  ```

### Windows
- Use PowerShell or Windows Terminal for better compatibility
- Consider using WSL2 for the best experience

### Linux
- Most distributions work out of the box
- Ensure Python development headers are installed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev

  # Fedora/RHEL
  sudo dnf install python3-devel
  ```

## Next Steps

Now that you have MockLLM installed, continue to:

- [Quick Start Guide](quick-start.md) to run your first mock server
- [Basic Usage](basic-usage.md) to learn about common operations
- [Configuration Guide](../configuration/responses.md) to set up response mappings