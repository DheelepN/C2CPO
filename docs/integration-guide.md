# C2CPO Integration Guide — Tier 1 & Tier 2

This guide walks you through integrating the C2CPO SDK into your internal service-to-service API architecture in the shortest possible time.

## Prerequisites

- **Python 3.10+** or **Node.js 18+**
- Internal services where you control both the producer (sender) and consumer (receiver)
- For Tier 2: a secrets management solution (environment variable, HashiCorp Vault, or cloud KMS)

## Architecture Overview

```
┌──────────────┐      C2CPO Encoded       ┌──────────────┐
│   Producer   │ ────────────────────────► │   Consumer   │
│   Service    │    (obfuscated JSON)      │   Service    │
│              │                           │              │
│  ┌────────┐  │                           │  ┌────────┐  │
│  │ C2CPO  │  │                           │  │ C2CPO  │  │
│  │Encoder │  │                           │  │Decoder │  │
│  └────────┘  │                           │  └────────┘  │
└──────────────┘                           └──────────────┘
       │                                          │
       ▼                                          ▼
  ┌─────────┐                              ┌──────────┐
  │   Key   │                              │ Anomaly  │
  │ Manager │                              │ Detector │
  └─────────┘                              └──────────┘
                                                  │
                                                  ▼
                                           ┌──────────┐
                                           │   SIEM   │
                                           └──────────┘
```

## Step 1 — Install

```bash
# Python
pip install c2cpo

# Node.js
npm install c2cpo
```

## Step 2 — Choose Your Tier

| Environment | Recommended Tier | Key Management Required |
|-------------|-----------------|------------------------|
| Development | Tier 1 | None |
| Staging / QA | Tier 1 or 2 | Environment variable |
| Production (non-critical) | Tier 2 | Vault / KMS |
| Production (security-sensitive) | Tier 3+ (contact us) | HSM |

## Step 3 — Tier 1 Integration (Zero Dependencies)

### Python — Producer

```python
from c2cpo import Tier1

encoder = Tier1(endpoint_id="payment-service")

# Encode payload before sending to the consumer service
payload = {"amount": 1000, "user_id": "usr_123", "currency": "USD"}
encoded = encoder.encode(payload)
# → {"XR7F2K9Q": 1000, "U9B3MX1P": "usr_123", "C7X9T1W0": "USD"}

# Send `encoded` to the consumer (via requests, httpx, etc.)
```

### Python — Consumer

```python
from c2cpo import Tier1
from c2cpo.exceptions import C2CPOFormatViolationError

decoder = Tier1(endpoint_id="payment-service")

# In your request handler:
raw_body = request.get_data(as_text=True)
try:
    decoded = decoder.decode(
        payload=request.json,
        raw_request_str=raw_body,
        source_ip=request.remote_addr,
    )
    # decoded → {"amount": 1000, "user_id": "usr_123", "currency": "USD"}
    process_payment(decoded)

except C2CPOFormatViolationError:
    # Standard REST request detected — attacker blocked, SIEM event emitted
    return '', 400
```

### Node.js — Producer

```typescript
import { Tier1 } from 'c2cpo';

const encoder = new Tier1('payment-service');
const encoded = encoder.encode({ amount: 1000, user_id: 'usr_123', currency: 'USD' });
// → { XR7F2K9Q: 1000, U9B3MX1P: 'usr_123', C7X9T1W0: 'USD' }
```

### Node.js — Consumer

```typescript
import { Tier1, C2CPOFormatViolationError } from 'c2cpo';

const decoder = new Tier1('payment-service');

app.post('/api/payment', (req, res) => {
  const rawBody = JSON.stringify(req.body);
  try {
    const decoded = decoder.decode(req.body, rawBody, req.ip);
    processPayment(decoded);
    res.json({ status: 'success' });
  } catch (e) {
    if (e instanceof C2CPOFormatViolationError) {
      return res.status(400).send('');  // Fail-closed, SIEM event already emitted
    }
    res.status(500).send('');
  }
});
```

## Step 4 — Tier 2 Integration (Value Encoding)

Tier 2 adds value-level obfuscation on top of Tier 1. Requires a shared master secret.

### Set up the master secret

```bash
# Generate a strong 32-byte (64 hex characters) random key
python -c "import secrets; print(secrets.token_hex(32))"

# Set as environment variable on both producer and consumer
export C2CPO_MASTER_SECRET="your-64-char-hex-output-here"
```

### Python

```python
from c2cpo import Tier2, KeyManager

key_manager = KeyManager()
secret = key_manager.get_master_key()

encoder = Tier2(endpoint_id="payment-service", master_secret=secret)
encoded = encoder.encode({"amount": 1000, "user_id": "usr_123"})
# → {"XR7F2K9Q": "RS", "U9B3MX1P": "4A2B8C1D9E3F"}
```

### Node.js

```typescript
import { Tier2, KeyManager } from 'c2cpo';

const secret = await new KeyManager().getMasterKey();
const encoder = new Tier2('payment-service', secret);
const encoded = encoder.encode({ amount: 1000, user_id: 'usr_123' });
```

### Using HashiCorp Vault

```bash
export VAULT_ADDR="https://vault.internal"
export VAULT_TOKEN="your-token"
```

```python
key_manager = KeyManager(use_vault=True)
secret = key_manager.get_master_key()
```

## Step 5 — Configure Anomaly Detection (Optional)

Push violation events to your SIEM via webhook:

```python
from c2cpo import Tier1

decoder = Tier1(
    endpoint_id="payment-service",
    webhook_url="https://siem.internal/c2cpo/alerts",
)
```

```typescript
const decoder = new Tier1('payment-service', 'https://siem.internal/c2cpo/alerts');
```

Events are always written to stdout regardless of webhook configuration.

## Step 6 — Monitoring

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| `FORMAT_VIOLATION` rate | Any occurrence | Investigate — automated attack or misconfigured producer |
| `DECODE_FAILURE` / `KEY_UNAVAILABLE` | Any occurrence | Fail-closed active — check key backend |

## Distributed Tracing

The following headers are passed through the encoder **unmodified** at all tiers:
- `traceparent`, `tracestate` (W3C Trace Context)
- `b3` (Zipkin B3)
- `X-Request-ID`, `X-Correlation-ID`

No additional configuration needed.

## Kubernetes

```yaml
containers:
- name: app
  image: your-service:latest
  env:
  - name: C2CPO_MASTER_SECRET
    valueFrom:
      secretKeyRef:
        name: c2cpo-secrets
        key: master-key
```
