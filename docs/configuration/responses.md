# Response Configuration

MockLLM uses YAML files to configure response mappings. This allows you to define exactly what responses the mock server should return for specific inputs.

## Basic Structure

A response configuration file has three main sections:

```yaml
responses:
  # Input-to-output mappings
  "prompt text": "response text"

defaults:
  # Default settings
  unknown_response: "Default response for unknown inputs"

settings:
  # Server behavior settings
  lag_enabled: true
  lag_factor: 10
```

## Response Mappings

### Simple Mappings

Map exact input text to responses:

```yaml
responses:
  "Hello": "Hi there!"
  "How are you?": "I'm doing great, thanks for asking!"
  "What is Python?": "Python is a high-level programming language."
```

## Default Responses

Configure fallback responses for unmatched inputs:

```yaml
defaults:
  unknown_response: "I don't have a specific response for that question."
```

## Settings

### Network Lag Simulation

Simulate realistic network latency:

```yaml
settings:
  lag_enabled: true    # Enable/disable lag simulation
  lag_factor: 10       # Higher = faster (1-100)
```

## Hot Reloading

MockLLM automatically detects changes to response files:

1. Start the server: `mockllm start --responses responses.yml`
2. Edit `responses.yml` in another terminal
3. Save the file - MockLLM reloads automatically
4. Test the new responses immediately

## Examples

### Customer Service Bot

```yaml
responses:
  "hours": "We're open Monday-Friday, 9 AM to 5 PM EST."
  "return policy": "You can return items within 30 days for a full refund."
  "shipping": "We offer free shipping on orders over $50."

defaults:
  unknown_response: "I'll connect you with a customer service representative."
```

## Validation

Validate your configuration file:

```bash
mockllm validate responses.yml
```

## Next Steps

- [Server Settings](settings.md) - Configure server behavior
- [Environment Variables](environment.md) - Set up environment configuration
- [Examples](../examples/testing.md) - See response configurations in action