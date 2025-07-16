# Sensor Key Registry - API Usage Examples

This document shows how to verify keys from sensor-data-service using the key registry.

## Quick Start

### 1. Using cURL (Command Line)

**Verify a public key:**
```bash
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -d '{
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
  }'
```

**Check registry status:**
```bash
curl http://localhost:8003/
```

**Get registry information:**
```bash
curl http://localhost:8003/keys/info
```

### 2. Using Python requests

```python
import requests

response = requests.post('http://localhost:8003/validate', json={
    'public_key_pem': your_public_key_string
})

result = response.json()
if result['is_valid']:
    print(f"Key is valid! Index: {result['key_index']}")
else:
    print("Key is not registered")
```

### 3. Using JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function verifyKey(publicKeyPem) {
    const response = await fetch('http://localhost:8003/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key_pem: publicKeyPem })
    });
    
    const result = await response.json();
    return result.is_valid;
}
```

## Integration Workflow

### Typical Usage Pattern:

1. **Receive data from sensor-data-service** (includes public key)
2. **Verify the key** against this registry
3. **Process data** only if key is valid

```python
# Example integration
def process_sensor_data(sensor_response):
    public_key = sensor_response['public_key']
    
    # Verify against registry
    verification = requests.post('http://localhost:8003/validate', 
                               json={'public_key_pem': public_key})
    
    if verification.json()['is_valid']:
        # Key is legitimate, process the data
        return process_trusted_data(sensor_response)
    else:
        # Key not registered, reject data
        raise SecurityError("Untrusted key source")
```

## Response Format

### Success Response (200):
```json
{
  "is_valid": true,
  "key_index": 2,
  "message": "Key matches registered key at index 2"
}
```

### Invalid Key (400):
```json
{
  "detail": "Invalid public key format. Expected RSA public key in PEM format."
}
```

### Key Not Found (200):
```json
{
  "is_valid": false,
  "key_index": null,
  "message": "Public key does not match any registered keys"
}
```

## Testing

Run the integration examples:
```bash
# Complete integration test
python utils/integration_example.py

# API functionality tests
python utils/test_api.py

# Manual key verification
python utils/client_example.py
```
