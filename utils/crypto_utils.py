import os
import json
import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from utils.config import logger, KEY_DIR

KEY_DIR = "keys"
NUM_KEYS = 5 

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
    logger.info(f"Signed sensor data with PKCS1v15: {base64.b64encode(signature).decode("utf-8")}")
    return base64.b64encode(signature).decode("utf-8")

def generate_keys_if_missing():
    os.makedirs(KEY_DIR, exist_ok=True)

    existing = [
        f for f in os.listdir(KEY_DIR)
        if f.endswith("_private.pem")
    ]

    if len(existing) >= NUM_KEYS:
        print(f"[KeyInit] Found {len(existing)} private keys. No new keys needed.")
        return

    print(f"[KeyInit] Generating {NUM_KEYS - len(existing)} new key(s)...")

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

        print(f"[KeyInit] Saved key pair: key_{i}")