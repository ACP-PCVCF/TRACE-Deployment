import os
import json
import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from config import logger, KEY_DIR

def load_private_key(sensor_id: str):
    path = os.path.join(KEY_DIR, f"{sensor_id}_private.pem")
    logger.info(f"Loading private key for sensor: {sensor_id}")
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def sign_data(data: dict, private_key) -> str:
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode("utf-8")
