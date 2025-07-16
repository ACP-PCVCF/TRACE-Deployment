import os
import json
import base64
import string
import secrets

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from utils.config import logger, KEY_DIR

KEY_DIR = "keys"
NUM_KEYS = 5


def generate_random_string(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    result = ''.join(secrets.choice(alphabet) for i in range(length))
    return result


def load_private_key(path: str):
    logger.info(f"Loading private key from: {path}")
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def get_all_private_key_paths():
    return [os.path.join(KEY_DIR, f) for f in os.listdir(KEY_DIR) if f.endswith("_private.pem")]


def sign_data(data: str, private_key) -> str:
    message = data.encode("utf-8")
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    logger.info(
        f"Signed sensor data with PKCS1v15: {base64.b64encode(signature).decode("utf-8")}")
    return base64.b64encode(signature).decode("utf-8")


def generate_hash(data: str) -> str:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data.encode("utf-8"))
    return base64.b64encode(digest.finalize()).decode("utf-8")


def generate_keys_if_missing():
    os.makedirs(KEY_DIR, exist_ok=True)

    existing = [
        f for f in os.listdir(KEY_DIR)
        if f.endswith("_private.pem")
    ]

    if len(existing) >= NUM_KEYS:
        logger.info(
            f"[KeyInit] Found {len(existing)} existing private keys. No generation needed.")
        return

    # Only generate if keys are truly missing
    logger.warning(
        f"[KeyInit] Only {len(existing)} keys found, expected {NUM_KEYS}. Generating {NUM_KEYS - len(existing)} new key(s)...")

    next_index = len(existing)
    for i in range(next_index, NUM_KEYS):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        priv_path = os.path.join(KEY_DIR, f"key_{i}_private.pem")
        pub_path = os.path.join(KEY_DIR, f"key_{i}_public.pem")

        with open(priv_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(pub_path, "wb") as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        logger.info(f"[KeyInit] Generated and saved key pair: key_{i}")

    logger.info(f"[KeyInit] Key generation complete. Total keys: {NUM_KEYS}")
