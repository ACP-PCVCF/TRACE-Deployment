import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = FastAPI(
    title="Sensor Key Registry",
    description="API service to validate public keys against registered sensor keys",
    version="1.0.0"
)

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
NUM_KEYS = 5


class PublicKeyRequest(BaseModel):
    public_key_pem: str


class ValidationResponse(BaseModel):
    is_valid: bool
    key_index: Optional[int] = None
    message: str


def load_registered_public_keys() -> List[bytes]:
    """Load all registered public keys from the keys directory."""
    public_keys = []

    if not os.path.exists(KEYS_DIR):
        return public_keys

    for i in range(NUM_KEYS):
        key_path = os.path.join(KEYS_DIR, f"key_{i}_public.pem")
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                public_keys.append(f.read())

    return public_keys


def normalize_pem_key(pem_data: str) -> bytes:
    """Normalize a PEM key string by removing extra whitespace and ensuring proper format."""
    lines = [line.strip()
             for line in pem_data.strip().split('\n') if line.strip()]
    normalized = '\n'.join(lines) + '\n'
    return normalized.encode('utf-8')


def validate_public_key_format(pem_data: str) -> bool:
    """Validate that the provided string is a valid RSA public key in PEM format."""
    try:
        key_bytes = pem_data.encode('utf-8')
        public_key = serialization.load_pem_public_key(key_bytes)
        # Verify it's an RSA key
        return isinstance(public_key, rsa.RSAPublicKey)
    except Exception:
        return False


@app.on_event("startup")
async def startup_event():
    """Load registered keys on startup."""
    registered_keys = load_registered_public_keys()
    app.state.registered_keys = registered_keys
    print(
        f"[KeyRegistry] Loaded {len(registered_keys)} registered public keys")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Sensor Key Registry",
        "status": "active",
        "registered_keys_count": len(getattr(app.state, 'registered_keys', []))
    }


@app.get("/keys/info")
async def get_keys_info():
    """Get information about registered keys."""
    registered_keys = getattr(app.state, 'registered_keys', [])
    return {
        "total_registered_keys": len(registered_keys),
        "expected_keys": NUM_KEYS,
        "keys_directory": KEYS_DIR
    }


@app.post("/validate", response_model=ValidationResponse)
async def validate_public_key(request: PublicKeyRequest):
    """
    Validate if the provided public key matches any of the registered sensor keys.

    Args:
        request: Contains the public key in PEM format to validate

    Returns:
        ValidationResponse indicating if the key is valid and its index if found
    """
    try:
        if not validate_public_key_format(request.public_key_pem):
            raise HTTPException(
                status_code=400,
                detail="Invalid public key format. Expected RSA public key in PEM format."
            )

        input_key_normalized = normalize_pem_key(request.public_key_pem)
        registered_keys = getattr(app.state, 'registered_keys', [])

        if not registered_keys:
            return ValidationResponse(
                is_valid=False,
                message="No registered keys found in the registry"
            )

        # Compare against each registered key
        for i, registered_key in enumerate(registered_keys):
            registered_key_normalized = normalize_pem_key(
                registered_key.decode('utf-8'))

            if input_key_normalized == registered_key_normalized:
                return ValidationResponse(
                    is_valid=True,
                    key_index=i,
                    message=f"Key matches registered key at index {i}"
                )

        return ValidationResponse(
            is_valid=False,
            message="Public key does not match any registered keys"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/keys/list")
async def list_registered_keys():
    """
    List all registered public keys (for debugging/admin purposes).
    Returns the keys in PEM format.
    """
    registered_keys = getattr(app.state, 'registered_keys', [])

    keys_list = []
    for i, key_data in enumerate(registered_keys):
        keys_list.append({
            "index": i,
            "key_pem": key_data.decode('utf-8')
        })

    return {
        "registered_keys": keys_list,
        "count": len(keys_list)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
