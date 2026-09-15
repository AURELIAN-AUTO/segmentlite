# SegmentLite 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/)
[![Live Hosted API](https://img.shields.io/badge/API-Live%20on%20Fly.io-emerald)](https://segmentlite-api-dfru.fly.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-success)](https://nodejs.org/)

**Lightweight, unbundled event routing and webhook fan-out API.**  
The 10x cheaper, developer-first alternative to Twilio Segment and RudderStack.

Live Cloud Sandbox & Docs: **[https://segmentlite-api-dfru.fly.dev](https://segmentlite-api-dfru.fly.dev)**

---

## 💡 Why SegmentLite?

| Feature | Twilio Segment | RudderStack Cloud | SegmentLite |
| :--- | :--- | :--- | :--- |
| **Starting Cost** | **$120 / mo** (scales fast) | **$349 / mo** | **$0 / mo** (Free tier) or **$19 flat / mo** |
| **Pricing Model** | Confusing MTU (Monthly Tracked Users) penalties | Volume + Seat tiers | Flat monthly quota (Zero MTU penalty) |
| **Delivery Latency** | 200ms - 800ms batching | Fast | **Sub-15ms edge async fan-out** |
| **Vendor Lock-In** | High (Heavy proprietary SDKs) | Moderate | **Zero (Standard REST, Webhooks & JSON)** |
| **Self-Hostable** | ❌ Proprietary SaaS | Complex (K8s/Postgres required) | ✅ **1-Line Docker Compose (SQLite)** |

---

## ⚡ 30-Second Quickstart

### 1. Ingest an Event (cURL)
```bash
curl -X POST "https://segmentlite-api-dfru.fly.dev/v1/track" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "Subscription Upgraded",
    "user_id": "usr_1029",
    "properties": {
      "plan": "Pro Annual",
      "amount": 190.00
    }
  }'
```

### 2. Python SDK
```python
from sdk.python.segmentlite import SegmentLite

client = SegmentLite(api_key="YOUR_API_KEY", host="https://segmentlite-api-dfru.fly.dev")

# Track event
client.track("Order Completed", user_id="usr_881", properties={"revenue": 49.99})

# Identify user traits
client.identify("usr_881", traits={"email": "dan@example.com", "tier": "enterprise"})
```

### 3. TypeScript / Node.js SDK
```typescript
import { SegmentLite } from 'segmentlite';

const client = new SegmentLite({
  apiKey: 'YOUR_API_KEY',
  host: 'https://segmentlite-api-dfru.fly.dev'
});

await client.track('Signed Up', {
  userId: 'usr_881',
  properties: { source: 'github' }
});
```

---

## 🐳 Self-Hosting in 1 Command

Run your own sovereign event router on any VPS, Hetzner, or Fly.io instance:

```bash
docker compose up -d
```

Or via Docker CLI:
```bash
docker run -d -p 8000:8000 --name segmentlite -v $(pwd)/data:/data segmentlite
```

Visit `http://localhost:8000` to access the interactive web sandbox and Swagger docs at `http://localhost:8000/docs`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/track` | Ingests event and dispatches background fan-out |
| `POST` | `/v1/identify` | Associates user identity traits across destinations |
| `POST` | `/v1/destinations` | Registers a new webhook or alert destination |
| `GET` | `/v1/destinations` | Lists all active routing destinations |
| `DELETE` | `/v1/destinations/{id}` | Removes a destination |
| `GET` | `/v1/stats` | Real-time event counts and delivery success metrics |
| `POST` | `/v1/auth/signup` | Self-service developer provisioning with instant API key |

---

## 📄 License
MIT License. Free for commercial and personal use.
