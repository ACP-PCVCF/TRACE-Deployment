#!/bin/bash

echo "Testing Key Registry API with cURL"
echo "=================================="

# Read the public key and properly escape it for JSON
KEY_CONTENT=$(cat keys/key_0_public.pem | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')

echo "Using key_0_public.pem for validation..."
echo ""

# Make the cURL request
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{\"public_key_pem\": \"$KEY_CONTENT\"}" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s

echo ""
echo "=================================="
echo "You can also test with different keys:"
echo "  sed 's/key_0/key_1/g' test_curl.sh | bash"
echo "  sed 's/key_0/key_2/g' test_curl.sh | bash"
