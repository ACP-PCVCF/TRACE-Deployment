import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"


class KeyRegistryClient:
    """Client for interacting with the Key Registry API."""

    def __init__(self, base_url: str = "http://localhost:8003"):
        """Initialize the client with the registry API URL."""
        self.base_url = base_url.rstrip('/')

    def validate_key(self, public_key_pem: str) -> dict:
        """
        Validate a public key against the registry.

        Args:
            public_key_pem: The public key in PEM format to validate

        Returns:
            dict: Validation result with is_valid, key_index, and message
        """
        try:
            response = requests.post(
                f"{self.base_url}/validate",
                json={"public_key_pem": public_key_pem}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "is_valid": False,
                "error": str(e),
                "message": "Failed to connect to key registry"
            }

    def get_service_info(self) -> dict:
        """Get information about the registry service."""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_keys_info(self) -> dict:
        """Get information about registered keys."""
        try:
            response = requests.get(f"{self.base_url}/keys/info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def example_usage():
    """Demonstrate how to use the KeyRegistryClient."""
    print("Key Registry Client Example")
    print("=" * 40)

    client = KeyRegistryClient()

    print("Service Info:")
    service_info = client.get_service_info()
    if "error" not in service_info:
        print(f"Service: {service_info.get('service', 'Unknown')}")
        print(f"Status: {service_info.get('status', 'Unknown')}")
        print(
            f"Registered Keys: {service_info.get('registered_keys_count', 0)}")
    else:
        print(f"Error: {service_info['error']}")
        return
    print("\nKeys Info:")
    keys_info = client.get_keys_info()
    if "error" not in keys_info:
        print(f"Total Keys: {keys_info.get('total_registered_keys', 0)}")
        print(f"Expected: {keys_info.get('expected_keys', 0)}")
    else:
        print(f"Error: {keys_info['error']}")

    # Load and validate a registered key
    print("\nTesting Key Validation:")
    try:
        # Read a sample key from the registry
        key_path = KEYS_DIR / "key_0_public.pem"
        with open(key_path, "r") as f:
            sample_key = f.read()

        print("   Testing with registered key...")
        result = client.validate_key(sample_key)

        if "error" not in result:
            print(f"   Valid: {result['is_valid']}")
            if result['is_valid']:
                print(f"   Key Index: {result.get('key_index', 'Unknown')}")
                print(f"   Message: {result.get('message', '')}")
        else:
            print(f"   Error: {result['error']}")

    except FileNotFoundError:
        print(
            "   Warning: No sample key found. Run 'python copy_keys.py --generate-sample' first.")
    except Exception as e:
        print(f"   Error reading sample key: {e}")


def validate_key_from_string(public_key_pem: str) -> bool:
    """
    Simple function to validate a public key.
    Returns True if valid, False otherwise.
    """
    client = KeyRegistryClient()
    result = client.validate_key(public_key_pem)
    return result.get('is_valid', False)


if __name__ == "__main__":
    example_usage()
