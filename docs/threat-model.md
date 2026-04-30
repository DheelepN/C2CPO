# C2CPO Threat Model

## System Boundaries

C2CPO protects **internal service-to-service** API communication. The threat model assumes:

- Attacker has valid network access (bypassed perimeter or insider)
- Attacker has valid credentials (authentication is not the defence)
- Both producer and consumer run the C2CPO SDK
- For Tier 2: master secret `K` is stored securely (Vault, KMS, or environment variable)

## Threat Matrix (Tiers 1 & 2)

| Threat | Tier 1 | Tier 2 |
|--------|--------|--------|
| Automated exploitation tools (SQLi, XSS, fuzzing, scanners) | **Blocked — P(detect) = 1.0** | **Blocked — P(detect) = 1.0** |
| Attacker with network capture only | Field mapping recoverable in ~1–3 hrs | Significantly harder — value encoding adds another layer |
| Attacker with SDK source code, no secret key | Static mapping trivially recoverable | HMAC pre-image search space: 2^256 |
| Attacker with SDK source + memory dump | Full compromise | Key extractable from memory — use KMS to mitigate |
| Replay attack | Not mitigated | Not mitigated |
| LLM-assisted reverse engineering | Significant risk | Reduced — HMAC tokens are semantically opaque |

> **Upgrade path:** Tiers 3 and 4 provide significantly stronger protection against skilled and LLM-assisted attackers. [Contact us](https://github.com/DheelepN/C2CPO/discussions) for enterprise tiers.

## Key Threats and Mitigations

### T1 — Automated Exploitation Tools
**Likelihood:** Very High — every exposed API is probed continuously  
**Impact:** Varies by endpoint  
**Mitigation:** FORMAT_VIOLATION detection at P = 1.0. Any tool sending standard field names is blocked and logged.  
**Residual Risk:** None for tools using standard REST/JSON format.

### T2 — Skilled Human Attacker
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:** Tier escalation. Tier 2 raises the human attacker barrier to ~3–8 hours.  
**Residual Risk:** Temporal barrier is theoretically grounded but empirically unvalidated for Tiers 1–2.

### T3 — LLM-Assisted Reverse Engineering
**Likelihood:** High — LLMs accelerate pattern recognition significantly  
**Impact:** Reduces Tier 1–2 barrier duration  
**Mitigation:** Tier 2 HMAC tokens are semantically opaque to LLMs without the key. Enterprise tiers provide stronger resistance.  
**Residual Risk:** LLMs with Tier 1 SDK source can reconstruct the mapping quickly.

### T4 — Supply Chain Compromise
**Likelihood:** Low but catastrophic  
**Impact:** Critical — silently defeats all tiers  
**Mitigation:** Signed releases, reproducible builds, dependency pinning, no secrets in source.  
**Residual Risk:** Determined nation-state attacker with build system access.

### T5 — Key Compromise (Tier 2)
**Likelihood:** Low with proper key management  
**Impact:** High — HMAC tokens become reconstructible  
**Mitigation:** Use Vault/KMS. Fail-closed if key is unavailable.  
**Residual Risk:** None if key is rotated before exploitation.

## What C2CPO Does NOT Protect Against

- **Public API attacks** — C2CPO requires the SDK on both sides (internal only)
- **Network-layer traffic analysis** — packet sizes and timing are not obfuscated
- **Authentication and authorisation bypasses** — C2CPO operates above this layer
- **Data at rest** — protects data in transit between services only
- **Denial of service** — not a DoS mitigation tool
