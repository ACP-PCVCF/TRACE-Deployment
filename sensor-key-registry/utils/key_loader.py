import os
from typing import List


KEYS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "keys")
NUM_KEYS = 5


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


def get_keys_directory() -> str:
    """Get the path to the keys directory."""
    return KEYS_DIR


def get_expected_keys_count() -> int:
    """Get the expected number of keys."""
    return NUM_KEYS
