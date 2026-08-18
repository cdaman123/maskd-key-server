# Maskd Key Server

This is the backend server responsible for securely serving the model decryption key to authorized `maskd` client containers.

## Features
- **Admin Panel**: Manage authorized License/API Keys via a Web UI (built with Flask-Admin).
- **PostgreSQL Database**: Persistent storage for license keys.
- **HMAC Request Signing**: Requests are signed using a hidden `APP_SECRET` embedded in the client binary.
- **Anti-Replay Protection**: Validates timestamps to prevent request replay attacks.

## Running with Docker Compose (Recommended)

To start the Key Server and the PostgreSQL database:

```bash
docker-compose up -d --build
```

### Accessing the Admin Panel
1. Navigate to: `http://localhost:5000/admin`
2. Login with credentials:
   - Username: `admin` (or whatever `ADMIN_USERNAME` is set to in `.env/docker-compose.yml`)
   - Password: `admin123` (or whatever `ADMIN_PASSWORD` is set to in `.env/docker-compose.yml`)
3. Create a new API Key (License Key). Provide this key to your client.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://maskd_user:maskd_pass@db:5432/maskd_keys` | PostgreSQL connection URI |
| `ADMIN_USERNAME` | `admin` | Admin panel login username |
| `ADMIN_PASSWORD` | `admin123` | Admin panel login password |
| `APP_SECRET` | `default-dev-app-secret-do-not-use-in-prod` | Secret used by client to sign requests. Must match `maskd` binary. |
| `MODEL_DECRYPTION_KEY_B64` | `MDEyMz...` | Actual AES key used to decrypt the models (base64 encoded). |

