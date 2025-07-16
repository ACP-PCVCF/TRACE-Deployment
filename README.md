# Sensor Key Registry

A FastAPI microservice for validating RSA public keys against a registry of known sensor keys.

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run the service**: `uvicorn main:app --reload --host 0.0.0.0 --port 8003`
3. **Test the API**: `python utils/test_api.py`

The service will be available at `http://localhost:8003`

## Project Structure

```
sensor-key-registry/
├── main.py              # FastAPI application
├── docs/                # Documentation files
│   ├── API_USAGE.md     # API usage examples
│   └── CURL_EXAMPLES.md # cURL command examples
├── utils/               # Utility modules
│   ├── copy_keys.py     # Key synchronization
│   ├── test_api.py      # API tests
│   ├── client_example.py # Usage examples
│   └── integration_example.py # Integration workflows
├── keys/                # Public key files
├── k8s/                 # Kubernetes deployment
└── requirements.txt     # Dependencies
```

## Documentation

- **[API Usage Examples](docs/API_USAGE.md)** - Integration examples for different languages
- **[cURL Examples](docs/CURL_EXAMPLES.md)** - Command-line testing examples

## API Endpoints

- `GET /` - Health check
- `GET /keys/info` - Registry information
- `POST /validate` - Validate a public key
- `GET /keys/list` - List all registered keys

## Quick Test

```bash
# Test with cURL
./test_curl.sh

# Test with Python
python utils/test_api.py
```

