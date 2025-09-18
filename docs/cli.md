# CLI Reference

MockLLM provides a comprehensive command-line interface for managing your mock LLM server.

## Global Options

```bash
mockllm [OPTIONS] COMMAND [ARGS]...
```

### Options

- `--version` - Show the version and exit
- `--help` - Show help message and exit

## Commands

### `mockllm start`

Start the MockLLM server.

```bash
mockllm start [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-r, --responses` | PATH | `responses.yml` | Path to responses YAML file |
| `-h, --host` | TEXT | `0.0.0.0` | Host to bind the server to |
| `-p, --port` | INTEGER | `8000` | Port to bind the server to |
| `--reload` | FLAG | `True` | Enable auto-reload on file changes |
| `--help` | FLAG | - | Show help message |

#### Examples

```bash
# Start with default settings
mockllm start

# Use custom responses file
mockllm start --responses my-responses.yml

# Bind to specific host and port
mockllm start --host localhost --port 3000

# Start without auto-reload
mockllm start --no-reload

# Combine options
mockllm start -r custom.yml -h 127.0.0.1 -p 8080
```

### `mockllm validate`

Validate a responses YAML file for syntax and structure.

```bash
mockllm validate RESPONSES_FILE
```

#### Arguments

- `RESPONSES_FILE` - Path to the responses YAML file to validate (required)

#### Examples

```bash
# Validate default file
mockllm validate responses.yml

# Validate custom file
mockllm validate path/to/my-responses.yml
```

#### Output

Success:
```
✓ Valid responses file
Found 10 responses
```

Error:
```
✗ Invalid responses file
YAML file must contain 'responses' key
```

## Environment Variables

MockLLM respects the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MOCKLLM_RESPONSES_FILE` | Default responses file path | `responses.yml` |
| `MOCKLLM_HOST` | Default server host | `0.0.0.0` |
| `MOCKLLM_PORT` | Default server port | `8000` |
| `MOCKLLM_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Examples

```bash
# Set default responses file
export MOCKLLM_RESPONSES_FILE=/path/to/responses.yml
mockllm start  # Uses the environment variable

# Override with command-line option
export MOCKLLM_PORT=3000
mockllm start --port 8080  # Uses 8080 (CLI overrides env)

# Set log level
export MOCKLLM_LOG_LEVEL=DEBUG
mockllm start  # Verbose logging
```

## Configuration File Support

While not required, you can create a `.mockllm` configuration file in your project root:

```yaml
# .mockllm
responses: custom-responses.yml
host: localhost
port: 8000
reload: true
log_level: INFO
```

Priority order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Advanced Usage

### Running in Docker

```bash
# Using the CLI in Docker
docker run -v $(pwd):/app mockllm/mockllm mockllm start --responses /app/responses.yml

# With environment variables
docker run -e MOCKLLM_PORT=3000 -p 3000:3000 mockllm/mockllm mockllm start
```

### Running with systemd

Create `/etc/systemd/system/mockllm.service`:

```ini
[Unit]
Description=MockLLM Server
After=network.target

[Service]
Type=exec
User=mockllm
WorkingDirectory=/opt/mockllm
ExecStart=/usr/local/bin/mockllm start --responses /opt/mockllm/responses.yml
Restart=always
Environment="MOCKLLM_LOG_LEVEL=INFO"

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mockllm
sudo systemctl start mockllm
```

### Running with PM2

```bash
# Install PM2
npm install -g pm2

# Start MockLLM
pm2 start "mockllm start" --name mockllm

# With custom settings
pm2 start "mockllm start --port 3000" --name mockllm-3000

# Save configuration
pm2 save
pm2 startup
```

### Using with Make

Create a `Makefile`:

```makefile
.PHONY: server validate test

server:
	mockllm start --responses responses.yml

validate:
	mockllm validate responses.yml

test:
	mockllm validate test-responses.yml
	mockllm start --responses test-responses.yml &
	pytest tests/
	pkill -f mockllm
```

## Shell Completion

Enable shell completion for better CLI experience:

### Bash

```bash
# Add to ~/.bashrc
eval "$(_MOCKLLM_COMPLETE=bash_source mockllm)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_MOCKLLM_COMPLETE=zsh_source mockllm)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
eval (env _MOCKLLM_COMPLETE=fish_source mockllm)
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
mockllm start --port 8001
```

### Permission Denied

```bash
# Use a port above 1024 (no root required)
mockllm start --port 8080

# Or use sudo (not recommended)
sudo mockllm start --port 80
```

### Configuration Not Loading

```bash
# Check file exists and is readable
ls -la responses.yml

# Validate the file
mockllm validate responses.yml

# Use absolute path
mockllm start --responses /absolute/path/to/responses.yml
```

## Integration Examples

### GitHub Actions

```yaml
name: Test with MockLLM
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install MockLLM
        run: pip install mockllm

      - name: Validate responses
        run: mockllm validate test-responses.yml

      - name: Start MockLLM
        run: |
          mockllm start --responses test-responses.yml &
          sleep 2

      - name: Run tests
        run: pytest tests/
```

### Docker Compose

```yaml
version: '3.8'

services:
  mockllm:
    image: mockllm/mockllm:latest
    command: mockllm start --responses /config/responses.yml
    ports:
      - "8000:8000"
    volumes:
      - ./responses.yml:/config/responses.yml
    environment:
      - MOCKLLM_LOG_LEVEL=INFO
```

## Exit Codes

MockLLM uses standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command or arguments |
| 3 | Configuration error |
| 4 | File not found |
| 5 | Port already in use |

## Getting Help

```bash
# General help
mockllm --help

# Command-specific help
mockllm start --help
mockllm validate --help

# Version information
mockllm --version
```

## Next Steps

- [Configuration Guide](configuration/responses.md) - Set up response mappings
- [Quick Start](getting-started/quick-start.md) - Get started quickly
- [Examples](examples/testing.md) - See MockLLM in action