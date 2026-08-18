# Key Server Security Architecture

This document explains the specific security layers implemented on the **Key Server** to ensure that model decryption keys are served securely and cannot be requested by unauthorized actors.

## 1. Cryptographic Request Validation (HMAC-SHA256)
The Key Server does not rely on simple API tokens or IP whitelisting. Instead, it enforces a strict **HMAC-SHA256 cryptographic signature** on every request.
* **Mechanism:** When a request hits the `/api/v1/models/key` endpoint, the Key Server takes the `X-License-Key` and `X-Timestamp` headers and computes an expected hash using its own secure `APP_SECRET`.
* **Security Benefit:** Even if an attacker steals a client's License Key, they cannot fetch the model decryption key unless they also possess the heavily obfuscated `APP_SECRET` to correctly sign the payload.

## 2. Anti-Replay Protection (Timestamp Drift)
A common vulnerability in static payload signing is a "Replay Attack," where an attacker intercepts a legitimate, signed network request and simply resends it later to extract the payload again.
* **Mechanism:** The Key Server enforces strict temporal bounds. It reads the `X-Timestamp` header and calculates the difference against the server's current UTC time.
* **Security Benefit:** If the timestamp is older than **30 seconds** (or comes from the future), the Key Server outright rejects the request. A captured request becomes useless almost instantly.

## 3. Database-Backed License Verification
Before serving the key, the server ensures the requesting entity actually has active permission to use the system.
* **Mechanism:** The Key Server performs a lookup in the PostgreSQL database for the provided `X-License-Key`.
* **Security Benefit:** You have granular, instantaneous control over client access. If a client's contract expires or their deployment is compromised, you can delete or deactivate their License Key from the Admin Panel, and the Key Server will immediately stop serving them the model keys.

## 4. Admin Panel Authentication
The interface used to generate and manage these licenses is tightly locked down.
* **Mechanism:** The `Flask-Admin` interface is protected via session-based authentication using `Flask-Login` and `Werkzeug` password hashing.
* **Security Benefit:** External actors cannot interact with the routing endpoints that modify or expose license keys without valid administrator credentials.

## 5. Transport Layer Security (TLS Pinning Readiness)
While the Key Server application handles application-layer logic, it is designed to be served behind an HTTPS reverse proxy (e.g., NGINX, AWS ALB, Cloudflare).
* **Mechanism:** The server delivers the AES-256 base64-encoded key strictly via the response body. 
* **Security Benefit:** Because the client application implements TLS Certificate Pinning, it guarantees that no Man-In-The-Middle (MITM) proxy can intercept the connection and read the AES key in transit. The Key Server will securely negotiate the encrypted tunnel directly with the verified application.
