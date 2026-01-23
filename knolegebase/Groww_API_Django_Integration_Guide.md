# Groww API — Django Integration Guide (Access Token Generation)

This guide explains how to **programmatically generate and manage Groww Access Tokens** inside a **Django backend application**, using **API Key + Secret + timestamp + checksum**.

This approach is **server-side only** and suitable for production Django projects.

---

## ⚠️ Security First (Non‑Negotiable)

- NEVER expose API Key, Secret, or Access Token to frontend
- NEVER commit secrets to Git
- Exclude `.env` from:
  - Git
  - AI tools (Augment, Copilot indexing)
- Rotate keys immediately if leaked

Groww **Access Tokens expire daily at 6:00 AM IST**.

---

## 1️⃣ Credentials Used by Groww

### Long‑lived (generated once)
- `GROWW_API_KEY`
- `GROWW_API_SECRET`

### Short‑lived (generated daily)
- `GROWW_ACCESS_TOKEN`

> You do **not refresh** the token.  
> You **re‑generate** it using Key + Secret.

---

## 2️⃣ Django Environment Setup

### `.env` (DO NOT COMMIT)

```env
GROWW_API_KEY=your_api_key
GROWW_API_SECRET=your_api_secret
```

### `settings.py`

```python
from dotenv import load_dotenv
import os

load_dotenv()

GROWW_API_KEY = os.getenv("GROWW_API_KEY")
GROWW_API_SECRET = os.getenv("GROWW_API_SECRET")
```

---

## 3️⃣ Checksum Logic (SHA‑256)

Groww verifies ownership using a deterministic SHA‑256 hash.

### Formula

```
checksum = SHA256(API_KEY + TIMESTAMP + API_SECRET)
```

- Timestamp must be in **milliseconds**
- Output must be **lowercase hex**

---

## 4️⃣ Django Utility Function (Recommended)

Create a utility file:

📁 `core/groww/auth.py`

```python
import time
import hashlib
import requests
from django.conf import settings

def generate_checksum(api_key, timestamp, api_secret):
    payload = f"{api_key}{timestamp}{api_secret}"
    return hashlib.sha256(payload.encode()).hexdigest()

def generate_access_token():
    timestamp = str(int(time.time() * 1000))
    checksum = generate_checksum(
        settings.GROWW_API_KEY,
        timestamp,
        settings.GROWW_API_SECRET
    )

    response = requests.post(
        "https://api.groww.in/auth/token",
        json={
            "apiKey": settings.GROWW_API_KEY,
            "timestamp": timestamp,
            "checksum": checksum,
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    return data["accessToken"]
```

> ⚠️ Verify endpoint URL and payload keys with **latest Groww docs** before deployment.

---

## 5️⃣ Token Storage Strategy (Best Practice)

### ❌ Do NOT
- Store token in database
- Store token in `.env`
- Log token

### ✅ DO
- Store token **in memory**
- Re‑generate on:
  - App startup
  - `401 Unauthorized`
  - Post‑6:00 AM IST

---

## 6️⃣ Simple Token Manager Pattern

📁 `core/groww/token_manager.py`

```python
from datetime import datetime, time as dtime
from .auth import generate_access_token

_access_token = None
_last_generated = None

def is_expired():
    now = datetime.now().time()
    return now >= dtime(6, 0)

def get_access_token():
    global _access_token, _last_generated

    if _access_token is None or is_expired():
        _access_token = generate_access_token()
        _last_generated = datetime.now()

    return _access_token
```

---

## 7️⃣ Using Token in API Calls

```python
from core.groww.token_manager import get_access_token
import requests

def place_order(payload):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.groww.in/orders",
        json=payload,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    return response.json()
```

---

## 8️⃣ Automation Options (Safe)

✔ Allowed:
- Django startup token generation
- Celery beat task after **6:01 AM IST**
- Regenerate on `401` error

❌ Not allowed:
- Username/password automation
- Frontend token generation
- Sharing tokens via logs or chat

---

## 9️⃣ Why This Works with Groww

- Matches Groww’s **documented authentication flow**
- No credential impersonation
- Enforces daily consent boundary
- Limits blast radius of leaks

---

## 🔚 One‑Line Summary

> In Django, Groww access tokens should be **generated server‑side using API Key + Secret + timestamp + SHA‑256 checksum**, stored only in memory, and re‑generated daily or on expiry.

---

### 🧠 Final Reminder
Security defines architecture.  
Automation must respect trust boundaries.
