import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"

BASE_URL = "http://localhost:8003"


def test_api_health():
    """Test the health check endpoint."""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"API is running: {data['service']}")
            print(f"Registered keys: {data['registered_keys_count']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Make sure the server is running.")
        return False


def test_keys_info():
    """Test the keys info endpoint."""
    print("\nTesting keys info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/keys/info")
        if response.status_code == 200:
            data = response.json()
            print("Keys info retrieved:")
            print(f"Total registered: {data['total_registered_keys']}")
            print(f"Expected keys: {data['expected_keys']}")
            return data['total_registered_keys'] > 0
        else:
            print(f"Keys info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error getting keys info: {e}")
        return False


def test_validate_registered_key():
    """Test validation with a key from the registry."""
    print("\nTesting validation with registered key...")

    try:
        response = requests.get(f"{BASE_URL}/keys/list")
        if response.status_code != 200:
            print("Could not retrieve registered keys for testing")
            return False

        keys_data = response.json()
        if not keys_data['registered_keys']:
            print("No registered keys found for testing")
            return False

        test_key = keys_data['registered_keys'][0]['key_pem']
        validation_response = requests.post(
            f"{BASE_URL}/validate",
            json={"public_key_pem": test_key}
        )

        if validation_response.status_code == 200:
            result = validation_response.json()
            if result['is_valid']:
                print("Key validation successful:")
                print(f"Valid: {result['is_valid']}")
                print(f"Key index: {result['key_index']}")
                print(f"Message: {result['message']}")
                return True
            else:
                print(
                    f"Registered key was marked as invalid: {result['message']}")
                return False
        else:
            print(
                f"Validation request failed: {validation_response.status_code}")
            return False

    except Exception as e:
        print(f"Error testing registered key validation: {e}")
        return False


def test_validate_invalid_key():
    """Test validation with an invalid key."""
    print("\nTesting validation with invalid key...")

    # Create a fake RSA public key for testing
    fake_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1234567890abcdefghij
klmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghij
klmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghij
klmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghij
klmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghij
klmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZwIDAQAB
-----END PUBLIC KEY-----"""

    try:
        validation_response = requests.post(
            f"{BASE_URL}/validate",
            json={"public_key_pem": fake_key}
        )

        if validation_response.status_code == 400:
            print("Invalid key properly rejected (400 Bad Request)")
            return True
        elif validation_response.status_code == 200:
            result = validation_response.json()
            if not result['is_valid']:
                print("Invalid key properly detected:")
                print(f"Valid: {result['is_valid']}")
                print(f"Message: {result['message']}")
                return True
            else:
                print(f"Invalid key was marked as valid: {result}")
                return False
        else:
            print(f"Unexpected response: {validation_response.status_code}")
            return False

    except Exception as e:
        print(f"Error testing invalid key: {e}")
        return False


def test_validate_sensor_service_key():
    """Test validation with a key directly from sensor-data-service format."""
    print("\nTesting validation with sensor-data-service key format...")

    # This simulates how someone would get a key from sensor-data-service
    # and then verify it against the registry
    try:
        key_path = KEYS_DIR / "key_0_public.pem"
        if key_path.exists():
            with open(key_path, "r") as f:
                sensor_key = f.read()

            print("Validating key received from sensor-data-service...")
            validation_response = requests.post(
                f"{BASE_URL}/validate",
                json={"public_key_pem": sensor_key}
            )

            if validation_response.status_code == 200:
                result = validation_response.json()
                if result['is_valid']:
                    print("Sensor service key validation successful:")
                    print(f"Valid: {result['is_valid']}")
                    print(f"Key index: {result['key_index']}")
                    print(f"Message: {result['message']}")
                    return True
                else:
                    print(
                        f"Sensor service key was marked as invalid: {result['message']}")
                    return False
            else:
                print(
                    f"Validation request failed: {validation_response.status_code}")
                return False
        else:
            print("No sensor service keys found for testing")
            return False

    except Exception as e:
        print(f"Error testing sensor service key validation: {e}")
        return False


def main():
    """Run all API tests."""
    print("Starting Key Registry API Tests")
    print("=" * 50)

    tests = [
        test_api_health,
        test_keys_info,
        test_validate_registered_key,
        test_validate_invalid_key,
        test_validate_sensor_service_key
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed!")
    else:
        print("Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
