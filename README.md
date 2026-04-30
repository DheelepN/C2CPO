<div align="center">
  <h1>🛡️ C2CPO</h1>
  <h3>Computer-to-Computer Protocol Obfuscation</h3>
  <p>
    The <strong>Machine-to-Machine (M2M) framework</strong> within the broader <strong>Security Linguistics</strong> academic domain (<a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6003235">read foundation paper</a>). The C2CPO framework itself is detailed <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6172085">in this SSRN preprint</a>. It is an open-source SDK that wraps internal service-to-service API communication in an obfuscated, custom-encoded protocol layer.
  </p>

  <p>
    <strong>Deterministic blocking of automated exploitation tools.</strong><br>
    <em>Raises the reverse-engineering barrier for human attackers.</em>
  </p>

  <div>
    <a href="https://github.com/DheelepN/C2CPO/actions"><img src="https://github.com/DheelepN/C2CPO/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg" alt="License: CC BY-NC 4.0"></a>
    <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
    <a href="https://nodejs.org"><img src="https://img.shields.io/badge/node.js-18%2B-green.svg" alt="Node.js 18+"></a>
  </div>
  <br>
</div>

---

## 📖 Table of Contents

1. [🔍 What This Is](#-what-this-is)
2. [💡 Why C2CPO vs. Traditional Methods?](#-why-c2cpo-vs-traditional-methods)
3. [🎯 What Is It Used For?](#-what-is-it-used-for)
4. [🏗️ Architecture: Where to Install It](#-architecture-where-to-install-it)
5. [📦 Exhaustive Installation Steps](#-exhaustive-installation-steps)
6. [🚀 Integration & Usage Guide](#-integration--usage-guide)
7. [🚨 Anomaly Detection (SIEM Integration)](#-anomaly-detection-siem-integration)
8. [🐳 Docker Demo](#-docker-demo)
9. [⚡ Performance & Benchmarks](#-performance--benchmarks)
10. [📚 Documentation & Enterprise Tiers](#-documentation--enterprise-tiers)
11. [📜 License & Citation](#-license--citation)

---

## 🔍 What This Is

**C2CPO** is the **Machine-to-Machine (M2M) framework** of the Security Linguistics domain. It functions as a **service-to-service security SDK** designed exclusively for internal infrastructure (e.g., backend microservices, cloud functions). 

Unlike traditional Web Application Firewalls (WAFs) or API Gateways that attempt to *probabilistically* guess if an incoming payload is malicious, C2CPO takes a **deterministic** approach. It scrambles the API contract itself. By mapping standard JSON payloads into an obfuscated format, **any request using standard, human-readable REST/JSON field names is immediately rejected.**

### 🛡️ The Two Security Properties

#### ① Automated attack detection — `P(detect) = 1.0`
SQLi scanners (like SQLMap), API fuzzers, and automated exploitation frameworks rely on standard JSON keys (e.g., `{"email": "admin@test.com"}`) to inject payloads. Because C2CPO expects `{"X9K2P1": "admin@test.com"}` instead, the automated tool fails on first contact. No signatures, no WAF rules, no calibration needed.

#### ② Human reverse-engineering barrier
A skilled attacker who has breached your perimeter and is sniffing internal network traffic faces a significant hurdle. They see obfuscated traffic and must spend hours reconstructing the mapping just to understand the data. The higher the C2CPO Tier, the longer this barrier becomes, giving your SOC time to detect and isolate the breach.

> **Honesty Note:** The human-attacker temporal barrier is theoretically grounded in the C2CPO v4.1 framework paper but is empirically unvalidated for Tiers 1–2. LLM-assisted attackers can reduce the Tier 1 barrier significantly. This is stated clearly in the framework paper.

---

## 💡 Why C2CPO vs. Traditional Methods?

When securing internal APIs, organizations typically rely on Network Segmentation, WAFs, and API Gateways. While essential, they have critical blind spots that C2CPO solves:

<details>
<summary><strong>1. The "Hard Shell, Soft Center" Problem</strong></summary>
<br>
Traditional methods focus entirely on the perimeter. If an attacker bypasses the external WAF (e.g., through an SSRF vulnerability or compromised developer credentials), the internal network is completely flat. An attacker can send standard REST queries (`GET /users?id=1' OR 1=1--`) directly to the backend. 
<br><br>
<strong>The C2CPO Difference:</strong> C2CPO hardens the internal services themselves. Even if the attacker is <em>inside</em> the network, their standard queries will bounce because the backend expects an obfuscated protocol language, not human-readable REST.
</details>

<details>
<summary><strong>2. Probabilistic vs. Deterministic Defense</strong></summary>
<br>
WAFs and API Gateways rely on <em>probabilistic</em> rules — regex signatures, AI/ML models, or rate limits — to guess if a payload is malicious. This leads to false positives (blocking legitimate traffic) and false negatives (failing to block zero-days).
<br><br>
<strong>The C2CPO Difference:</strong> C2CPO is <strong>100% deterministic</strong>. We do not look for "bad" characters like <code>&lt;script&gt;</code> or <code>' OR 1=1</code>. If the request is not encoded using the exact expected C2CPO mapping, it is instantly rejected as a Format Violation.
</details>

<details>
<summary><strong>3. Tooling Asymmetry</strong></summary>
<br>
Attackers rely heavily on automated tooling (Burp Suite, SQLMap, Postman, Nuclei). These tools are built to parse and inject into standard JSON (<code>{"email": "..."}</code>). 
<br><br>
<strong>The C2CPO Difference:</strong> By breaking the fundamental assumption of these tools (that the API speaks standard JSON), C2CPO immediately renders 100% of off-the-shelf automated exploitation tools completely useless. The attacker must switch to manual, painstaking reverse-engineering.
</details>

<br>

### ❌ What C2CPO Is *Not*
- Not a replacement for TLS, mutual TLS (mTLS), or authentication.
- Not for public-facing internet APIs (browsers and external clients cannot run the SDK).
- Not a multi-tenant SaaS protection tool.

---

## 🎯 What Is It Used For?

C2CPO is used to defend the **"soft underbelly"** of your backend network. It is designed to stop attackers who have already bypassed the perimeter from pivoting and exploiting your internal APIs.

**Primary Use Cases:**
- 🔗 **Microservice-to-Microservice Communication:** Secure data flowing between `PaymentService`, `UserService`, and `OrderService` within a Kubernetes cluster or VPC.
- ☁️ **Cloud Functions & Serverless:** Secure payloads sent from AWS API Gateway to internal Lambda functions, or GCP Cloud Run services.
- 🔐 **Zero-Trust Backend APIs:** Add a defense-in-depth layer to your internal APIs so that an insider threat cannot trivially fuzz or exploit your backend databases using standard tools.

---

## 🏗️ Architecture: Where to Install It

Because C2CPO alters the structure of the JSON payload, it **must be installed on both sides of the communication channel.**

*   📤 **The Producer (Sender):** The microservice or client making the API request. It uses the C2CPO SDK to `encode()` the standard JSON into an obfuscated payload before sending it over the network.
*   📥 **The Consumer (Receiver):** The microservice or server receiving the request. It uses the C2CPO SDK to `decode()` the obfuscated payload back into standard JSON before passing it to the application logic.

### Deployment Patterns
You do not need to rewrite your business logic! Integrate C2CPO at the edge of your service framework:
- **Python:** Inside a `FastAPI Middleware`, a `Flask before_request` hook, or an HTTP request wrapper like `requests`.
- **Node.js:** Inside an `Express.js middleware`, an `Axios request interceptor`, or a custom `fetch` wrapper.

---

## 📦 Exhaustive Installation Steps

C2CPO supports **Python (3.10+)** and **Node.js (18+)**. It is intentionally lightweight, with zero external dependencies for Tier 1.

<details>
<summary><strong>🐍 Installing for Python</strong></summary>
<br>

**Method 1: Using pip (Standard)**
```bash
pip install c2cpo
```

**Method 2: Using requirements.txt**
Add `c2cpo` to your `requirements.txt` file:
```text
c2cpo==1.0.0
```
Then install:
```bash
pip install -r requirements.txt
```

**Method 3: Using Poetry (Modern)**
```bash
poetry add c2cpo
```
</details>

<details>
<summary><strong>🟢 Installing for Node.js / TypeScript</strong></summary>
<br>

TypeScript definitions are included out of the box.

**Method 1: Using npm (Standard)**
```bash
npm install c2cpo
```

**Method 2: Using yarn**
```bash
yarn add c2cpo
```

**Method 3: Using pnpm**
```bash
pnpm add c2cpo
```
</details>

---

## 🚀 Integration & Usage Guide

### 🟢 Tier 1 — Field Name Obfuscation

Tier 1 provides immediate defense against automated tools. It maps standard JSON keys to deterministic, obfuscated keys. Zero external dependencies. No key management required.

<details>
<summary><strong>Python Integration Examples</strong></summary>
<br>

#### Producer (Sender)
```python
import requests
from c2cpo import Tier1

encoder = Tier1(endpoint_id="payment-service")

payload = {
    "amount": 1000,
    "user_id": "usr_123",
    "currency": "USD"
}

encoded_payload = encoder.encode(payload)
# Result: {"XR7F2K9Q": 1000, "U9B3MX1P": "usr_123", "C7X9T1W0": "USD"}

requests.post("http://internal-payment-service/charge", json=encoded_payload)
```

#### Consumer (Receiver - FastAPI)
```python
from fastapi import FastAPI, Request, HTTPException
from c2cpo import Tier1
from c2cpo.exceptions import C2CPOFormatViolationError

app = FastAPI()
decoder = Tier1(endpoint_id="payment-service")

@app.post("/charge")
async def charge_endpoint(request: Request):
    raw_body = await request.body()
    try:
        encoded_json = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        decoded = decoder.decode(
            payload=encoded_json,
            raw_request_str=raw_body.decode('utf-8'),
            source_ip=request.client.host
        )
    except C2CPOFormatViolationError:
        # Standard REST field detected — attacker blocked, SIEM event emitted!
        raise HTTPException(status_code=400, detail="C2CPO Violation")

    # Proceed with standard business logic
    return {"status": "success", "processed_amount": decoded["amount"]}
```
</details>

<details>
<summary><strong>Node.js Integration Examples</strong></summary>
<br>

#### Producer (Sender - Axios)
```typescript
import axios from 'axios';
import { Tier1 } from 'c2cpo';

const encoder = new Tier1('payment-service');

async function sendPayment() {
  const payload = { amount: 1000, user_id: 'usr_123', currency: 'USD' };
  const encodedPayload = encoder.encode(payload);
  
  await axios.post('http://internal-payment-service/charge', encodedPayload);
}
```

#### Consumer (Receiver - Express.js)
```typescript
import express from 'express';
import { Tier1, C2CPOFormatViolationError } from 'c2cpo';

const app = express();
app.use(express.json());

const decoder = new Tier1('payment-service');

app.post('/charge', (req, res) => {
  try {
    const decoded = decoder.decode(
      req.body, 
      JSON.stringify(req.body), 
      req.ip || 'unknown'
    );
    
    res.json({ status: 'success', processed: decoded.amount });

  } catch (e) {
    if (e instanceof C2CPOFormatViolationError) {
      return res.status(400).send('C2CPO Violation');
    }
    return res.status(500).send('Internal Server Error');
  }
});
```
</details>

---

### 🟡 Tier 2 — Custom Value Encoding

Tier 2 adds value-level obfuscation: integers become Base36 strings, strings become 12-character HMAC tokens.  
**Requirement:** You must share a master secret key between the producer and the consumer.

<details>
<summary><strong>Step 1: Generate & Set a Master Key</strong></summary>
<br>

Generate a strong key (32 bytes = 64 hex chars):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Set it as an environment variable on both Producer and Consumer:
```bash
export C2CPO_MASTER_SECRET="your-64-char-hex-string-from-above"
```
</details>

<details>
<summary><strong>Step 2: Implement (Python & Node.js)</strong></summary>
<br>

#### Python
```python
from c2cpo import Tier2, KeyManager

secret = KeyManager().get_master_key()
encoder = Tier2(endpoint_id="payment-service", master_secret=secret)

encoded = encoder.encode({"amount": 1000, "user_id": "usr_123"})
# Result: {"XR7F2K9Q": "RS", "U9B3MX1P": "4A2B8C1D9E3F"}
```

#### Node.js
```typescript
import { Tier2, KeyManager } from 'c2cpo';

async function run() {
  const secret = await new KeyManager().getMasterKey();
  const encoder = new Tier2('payment-service', secret);

  const encoded = encoder.encode({ amount: 1000, user_id: 'usr_123' });
  // Result: { XR7F2K9Q: 'RS', U9B3MX1P: '4A2B8C1D9E3F' }
}
```
</details>

<details>
<summary><strong>Advanced Key Management Backends</strong></summary>
<br>

C2CPO supports enterprise KMS backends out of the box:

| Backend | Setup Instructions |
|---------|--------------------|
| **Environment var** | `export C2CPO_MASTER_SECRET="64-char-hex"` |
| **HashiCorp Vault** | Provide `VAULT_ADDR` & `VAULT_TOKEN`. Use `KeyManager(use_vault=True)` |
| **AWS KMS** | Set `C2CPO_KMS_BACKEND=AWS`. Ensure IAM roles allow `kms:Decrypt`. |
| **Azure Key Vault** | Set `C2CPO_KMS_BACKEND=AZURE`. |
| **GCP KMS** | Set `C2CPO_KMS_BACKEND=GCP`. |
</details>

---

## 🚨 Anomaly Detection (SIEM Integration)

Whenever an attacker sends a standard payload (like `{"amount": 1000}`) instead of the obfuscated payload, C2CPO throws a `C2CPOFormatViolationError`.

It **automatically** writes a structured, single-line JSON event to `stdout`. This allows your standard logging agent (Fluentd, Promtail, Datadog Agent) to ingest the alert immediately.

```json
{
  "timestamp": "2026-04-30T07:22:00.000Z",
  "source_ip": "203.0.113.42",
  "endpoint_id": "payment-service",
  "violation_type": "FORMAT_VIOLATION",
  "severity": "HIGH",
  "failure_cause": "ATTACKER_PAYLOAD",
  "tier": 1
}
```

**Optional Webhook Push:** You can also tell C2CPO to POST directly to your SIEM via a webhook:
```python
decoder = Tier1(
    endpoint_id="payment-service",
    webhook_url="https://siem.internal/c2cpo/alerts"
)
```

---

## 🐳 Docker Demo

Want to see it in action without writing code? We provide a ready-to-run Docker Compose environment.

```bash
git clone https://github.com/DheelepN/C2CPO.git
cd c2cpo/demo
docker compose up
```

Watch the terminal logs to see an attacker getting blocked with a `FORMAT_VIOLATION`, while a legitimate Producer's encoded request is seamlessly accepted.

---

## ⚡ Performance & Benchmarks

Performance is a critical constraint for internal communications. C2CPO is extremely lightweight and is designed to meet strict Product Requirement Document (PRD) targets.

| Tier | Encode p50 | Encode p99 | PRD Target |
|------|-----------|-----------|------------|
| **Tier 1** (5 fields) | 0.003 ms | 0.003 ms | < 0.5 ms |
| **Tier 2** (5 fields) | 0.031 ms | 0.063 ms | < 2 ms |

Tier 1 adds effectively **zero** overhead (`< 0.01ms` latency).  
📊 *See [BENCHMARKS.md](BENCHMARKS.md) for exhaustive network benchmark results, medium/large payload scaling, and security efficacy metrics.*

---

## 📚 Documentation & Enterprise Tiers

| Document | Description |
|----------|-------------|
| 📖 [Integration Guide](docs/integration-guide.md) | Step-by-step framework integration |
| 🛡️ [Threat Model](docs/threat-model.md) | What C2CPO protects against (and what it doesn't) |
| 📈 [Benchmarks](BENCHMARKS.md) | Full latency and security efficacy metrics |
| 🧪 [Test Vectors](test-vectors/README.md) | Normative cross-SDK verification vectors |
| 🔒 [Security Policy](SECURITY.md) | Vulnerability reporting and safe harbour policies |
| 🤝 [Contributing](CONTRIBUTING.md) | How to contribute to the open-source SDK |

### 🏢 Enterprise Tiers (3 & 4)
**Tiers 3 and 4** build on this open-source foundation with additional protocol-layer manipulation (Synthetic Protocol Structure and Dynamic Epoch Evolution). These higher tiers are designed to exhaust even well-funded, persistent, skilled human attackers and LLM-assisted models.

> Interested in Enterprise Tiers? [Open a discussion](https://github.com/DheelepN/C2CPO/discussions) or contact [@DheelepN](https://github.com/DheelepN).

---

## 📜 License & Citation

**[CC BY-NC 4.0](LICENSE)** — Creative Commons Attribution-NonCommercial 4.0 International

- ✅ Free to use, modify, and redistribute **with attribution**
- ✅ Non-commercial use (research, personal projects, open-source) — no permission needed
- ❌ **Commercial use requires prior written permission** from the author

Contact [@DheelepN](https://github.com/DheelepN) to request a commercial license.

### 🎓 Academic Citation

**Framework paper:**
> N Dheelep Sai Gupthaa, *C2CPO: Computer-to-Computer Protocol Obfuscation v4.1*, SSRN:6172085, 2026.  
> [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6172085](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6172085)

**Parent research (Security Linguistics):**
> N Dheelep Sai Gupthaa, *Security Linguistics*, SSRN:6003235, 2026.  
> [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6003235](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6003235)
