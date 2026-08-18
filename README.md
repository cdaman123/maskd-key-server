# Maskd Key Server

This is the backend server responsible for securely serving the model decryption key to authorized `maskd` client containers.

## Security Architecture

To prevent unauthorized access to the models, this server uses:
1. **License Validation:** Clients must provide a valid `X-License-Key` header.
2. **HMAC Request Signing:** Requests are signed using a hidden `APP_SECRET` embedded in the client binary.
3. **Anti-Replay Protection:** The signed payload includes a timestamp (`X-Timestamp`) which is validated to ensure requests are not older than 30 seconds.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APP_SECRET="your-super-secret-app-secret"
export MODEL_DECRYPTION_KEY_B64="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="

# Run the server
flask --app app.main run --port 5000
```

## Docker Deployment

```bash
docker build -t maskd-key-server .
docker run -p 5000:5000 \
    -e APP_SECRET="your-super-secret-app-secret" \
    -e MODEL_DECRYPTION_KEY_B64="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=" \
    maskd-key-server
```
