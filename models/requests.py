from pydantic import BaseModel


class PublicKeyRequest(BaseModel):
    """Request model for public key validation."""
    public_key_pem: str
