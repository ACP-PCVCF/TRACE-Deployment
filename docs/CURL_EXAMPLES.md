# cURL Commands for Key Registry API Testing

## Method 1: Direct cURL with key_0_public.pem

```bash
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{\"public_key_pem\": \"$(cat keys/key_0_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
```

## Method 2: Using a JSON file (Recommended)

Create a JSON file with the key:
```bash
# Create JSON with key_1_public.pem
cat > test_key.json << EOF
{
  "public_key_pem": "$(cat keys/key_1_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')"
}
EOF

# Use the JSON file with cURL
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -d @test_key.json
```

## Method 3: One-liner for any key

```bash
# Test key_2_public.pem
KEY_FILE="keys/key_2_public.pem" && \
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -d "{\"public_key_pem\": \"$(cat $KEY_FILE | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
```

## Method 4: With pretty output

```bash
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -d "{\"public_key_pem\": \"$(cat keys/key_3_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n" | jq '.'
```

## Method 5: Test all keys at once

```bash
for i in {0..4}; do
  echo "Testing key_${i}_public.pem:"
  curl -X POST http://localhost:8003/validate \
    -H "Content-Type: application/json" \
    -d "{\"public_key_pem\": \"$(cat keys/key_${i}_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}" \
    -s | jq '.key_index, .message'
  echo ""
done
```

## Method 6: Test with an invalid key

```bash
curl -X POST http://localhost:8003/validate \
  -H "Content-Type: application/json" \
  -d '{
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\nINVALID_KEY_CONTENT\n-----END PUBLIC KEY-----"
  }'
```

## Other useful endpoints:

```bash
# Health check
curl http://localhost:8003/

# Registry info
curl http://localhost:8003/keys/info

# List all registered keys
curl http://localhost:8003/keys/list
```

## Copy-paste ready commands:

**Quick test with key_0:**
```bash
curl -X POST http://localhost:8003/validate -H "Content-Type: application/json" -d "{\"public_key_pem\": \"$(cat keys/key_0_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
```

**Quick test with key_1:**
```bash
curl -X POST http://localhost:8003/validate -H "Content-Type: application/json" -d "{\"public_key_pem\": \"$(cat keys/key_1_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
```

**Quick test with key_2:**
```bash
curl -X POST http://localhost:8003/validate -H "Content-Type: application/json" -d "{\"public_key_pem\": \"$(cat keys/key_2_public.pem | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
```
