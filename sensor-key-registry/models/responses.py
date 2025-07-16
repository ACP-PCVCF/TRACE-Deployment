from typing import Optional
from pydantic import BaseModel


class ValidationResponse(BaseModel):
    """Response model for key validation results."""
    is_valid: bool
    key_index: Optional[int] = None
    message: str


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    service: str
    status: str
    registered_keys_count: int


class KeysInfoResponse(BaseModel):
    """Response model for keys information endpoint."""
    total_registered_keys: int
    expected_keys: int
    keys_directory: str


class RegisteredKeyItem(BaseModel):
    """Model for individual registered key item."""
    index: int
    key_pem: str


class RegisteredKeysResponse(BaseModel):
    """Response model for listing all registered keys."""
    registered_keys: list[RegisteredKeyItem]
    count: int
