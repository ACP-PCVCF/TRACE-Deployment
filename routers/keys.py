from typing import List
from fastapi import APIRouter, HTTPException, Depends
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from models.requests import PublicKeyRequest
from models.responses import (
    ValidationResponse,
    KeysInfoResponse,
    RegisteredKeysResponse,
    RegisteredKeyItem
)
from utils.key_loader import get_keys_directory, get_expected_keys_count

router = APIRouter(prefix="/keys", tags=["keys"])


def get_registered_keys():
    """Dependency to get registered keys from app state."""
    from main import app
    return getattr(app.state, 'registered_keys', [])


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


@router.get("/info", response_model=KeysInfoResponse)
async def get_keys_info(registered_keys: List[bytes] = Depends(get_registered_keys)):
    """Get information about registered keys."""
    return KeysInfoResponse(
        total_registered_keys=len(registered_keys),
        expected_keys=get_expected_keys_count(),
        keys_directory=get_keys_directory()
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_public_key(
    request: PublicKeyRequest,
    registered_keys: List[bytes] = Depends(get_registered_keys)
):
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


@router.get("/list", response_model=RegisteredKeysResponse)
async def list_registered_keys(registered_keys: List[bytes] = Depends(get_registered_keys)):
    """
    List all registered public keys (for debugging/admin purposes).
    Returns the keys in PEM format.
    """
    keys_list = []
    for i, key_data in enumerate(registered_keys):
        keys_list.append(RegisteredKeyItem(
            index=i,
            key_pem=key_data.decode('utf-8')
        ))

    return RegisteredKeysResponse(
        registered_keys=keys_list,
        count=len(keys_list)
    )
