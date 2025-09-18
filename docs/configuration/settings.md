# Server Settings

Configure MockLLM server behavior and performance settings.

## Configuration File

Settings can be configured in your responses YAML file:

```yaml
settings:
  lag_enabled: true
  lag_factor: 10
  max_response_length: 1000
```

## Available Settings

### Network Simulation

- `lag_enabled`: Enable/disable network lag simulation
- `lag_factor`: Response speed (1-100, higher = faster)

### Response Limits

- `max_response_length`: Maximum characters in responses
- `timeout_seconds`: Request timeout

## Environment Variables

- `MOCKLLM_HOST`: Server host (default: 0.0.0.0)
- `MOCKLLM_PORT`: Server port (default: 8000)
- `MOCKLLM_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Next Steps

- [Response Configuration](responses.md)
- [Environment Variables](environment.md)