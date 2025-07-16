import requests
from pathlib import Path
from typing import Dict, Any, Optional


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"


class SensorKeyVerifier:
    """Client for verifying sensor service keys against the key registry."""

    def __init__(self, registry_url: str = "http://localhost:8003"):
        self.registry_url = registry_url.rstrip('/')

    def verify_key(self, public_key_pem: str) -> Dict[str, Any]:
        """
        Verify if a public key is registered and legitimate.

        Args:
            public_key_pem: The public key in PEM format received from sensor-data-service

        Returns:
            dict: Verification result with status and details
        """
        try:
            response = requests.post(
                f"{self.registry_url}/validate",
                json={"public_key_pem": public_key_pem}
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "is_valid": result['is_valid'],
                    "key_index": result.get('key_index'),
                    "message": result.get('message', ''),
                    "trusted": result['is_valid']
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "is_valid": False,
                    "error": "Invalid key format",
                    "trusted": False
                }
            else:
                return {
                    "success": False,
                    "is_valid": False,
                    "error": f"Registry service error: {response.status_code}",
                    "trusted": False
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "is_valid": False,
                "error": f"Connection error: {str(e)}",
                "trusted": False
            }

    def get_registry_info(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.registry_url}/")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None


def simulate_sensor_data_processing():
    verifier = SensorKeyVerifier()

    # Check if registry is available
    print("Checking key registry service...")
    registry_info = verifier.get_registry_info()
    if registry_info:
        print(f"Registry is online: {registry_info['service']}")
        print(f"Registered keys: {registry_info['registered_keys_count']}")
    else:
        print("ERROR: Key registry is not available!")
        return False

    simulated_sensor_response = {
        "sensor_id": "sensor_001",
        "data": "temperature:25.3,humidity:60.2",
        "signature": "base64_encoded_signature_here",
        "public_key": None,
        "timestamp": "2025-07-16T10:30:00Z"
    }

    # Load a test key
    try:
        key_path = KEYS_DIR / "key_2_public.pem"
        with open(key_path, "r") as f:
            simulated_sensor_response["public_key"] = f.read()
        print("Received sensor data with public key")
    except FileNotFoundError:
        print("ERROR: No test keys available. Run 'python utils/copy_keys.py' first")
        return False

    print("\nVerifying the public key against registry...")
    verification_result = verifier.verify_key(
        simulated_sensor_response["public_key"])

    if verification_result["success"]:
        if verification_result["is_valid"]:
            print("KEY VERIFIED: Public key is registered and trusted")
            print(f"Key index: {verification_result['key_index']}")
            print(f"Message: {verification_result['message']}")
            return True
        else:
            print("KEY REJECTED: Public key is not registered")
            print(f"Message: {verification_result['message']}")
            return False
    else:
        print(f"VERIFICATION FAILED: {verification_result['error']}")
        return False


def example_api_usage():
    """Show different ways to use the verification API."""
    print("\n" + "=" * 60)
    print("API USAGE EXAMPLES")
    print("=" * 60)

    verifier = SensorKeyVerifier()

    print("\nExample 1: Simple key verification")
    print("-" * 30)

    # Example with a legitimate key
    try:
        key_path = KEYS_DIR / "key_1_public.pem"
        with open(key_path, "r") as f:
            test_key = f.read()

        result = verifier.verify_key(test_key)
        print(f"Valid key result: {result}")

    except FileNotFoundError:
        print("No test keys available")

    print("\nExample 2: Invalid key handling")
    print("-" * 30)

    # Example with an invalid key
    fake_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA123456789invalid
-----END PUBLIC KEY-----"""

    result = verifier.verify_key(fake_key)
    print(f"Invalid key result: {result}")

    print("\nExample 3: Direct HTTP POST request")
    print("-" * 30)

    try:
        key_path = KEYS_DIR / "key_3_public.pem"
        with open(key_path, "r") as f:
            test_key = f.read()

        response = requests.post(
            "http://localhost:8003/validate",
            json={"public_key_pem": test_key}
        )
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    success = simulate_sensor_data_processing()
    example_api_usage()

    return success


if __name__ == "__main__":
    main()
