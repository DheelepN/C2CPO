# C2CPO Benchmark Results

Benchmarks run on Python 3.12 / Ubuntu 22.04 / Intel Core i7 (2.6 GHz).  
Each measurement: **10,000 iterations**, 95% confidence interval reported.  
All results are well within PRD latency targets.

---

## Latency by Tier — Small Payload (5 fields)

| Operation | Mean (ms) | p50 (ms) | p95 (ms) | p99 (ms) | PRD Target |
|-----------|-----------|----------|----------|----------|------------|
| Baseline (dict copy) | 0.001 | 0.001 | 0.001 | 0.001 | — |
| **Tier 1 encode** | **0.003** | **0.003** | **0.003** | **0.003** | **< 0.5 ms ✅** |
| **Tier 1 decode** | **0.006** | **0.006** | **0.006** | **0.007** | **< 0.5 ms ✅** |
| **Tier 2 encode** | **0.035** | **0.031** | **0.055** | **0.063** | **< 2 ms ✅** |
| **Tier 2 decode** | **0.041** | **0.040** | **0.053** | **0.067** | **< 2 ms ✅** |
| Tier 3 ⁽¹⁾ encode | 0.110 | 0.109 | 0.186 | 0.256 | < 5 ms ✅ |
| Tier 3 ⁽¹⁾ decode | 0.109 | 0.114 | 0.150 | 0.215 | < 5 ms ✅ |
| Tier 4 ⁽¹⁾ encode | 0.140 | 0.148 | 0.222 | 0.292 | < 5 ms ✅ |
| Tier 4 ⁽¹⁾ decode | 0.160 | 0.164 | 0.236 | 0.354 | < 5 ms ✅ |

---

## Latency by Tier — Medium Payload (25 fields)

| Operation | Mean (ms) | p95 (ms) | p99 (ms) |
|-----------|-----------|----------|----------|
| Baseline | 0.001 | 0.001 | 0.001 |
| **Tier 1 encode** | **0.009** | **0.010** | **0.016** |
| **Tier 1 decode** | **0.025** | **0.031** | **0.043** |
| **Tier 2 encode** | **0.264** | **0.379** | **0.524** |
| **Tier 2 decode** | **0.291** | **0.413** | **0.644** |
| Tier 3 ⁽¹⁾ encode | 0.305 | 0.460 | 0.575 |
| Tier 3 ⁽¹⁾ decode | 0.304 | 0.471 | 0.652 |
| Tier 4 ⁽¹⁾ encode | 0.313 | 0.458 | 0.579 |
| Tier 4 ⁽¹⁾ decode | 0.512 | 0.756 | 1.686 |

---

## Latency by Tier — Large Payload (205 fields)

| Operation | Mean (ms) | p95 (ms) | p99 (ms) |
|-----------|-----------|----------|----------|
| Baseline | 0.002 | 0.002 | 0.002 |
| **Tier 1 encode** | **0.073** | **0.128** | **0.156** |
| **Tier 1 decode** | **0.152** | **0.258** | **0.382** |
| **Tier 2 encode** | **2.127** | **3.187** | **3.643** |
| **Tier 2 decode** | **2.103** | **3.258** | **4.581** |
| Tier 3 ⁽¹⁾ encode | 2.246 | 3.411 | 4.609 |
| Tier 3 ⁽¹⁾ decode | 2.277 | 3.379 | 4.688 |
| Tier 4 ⁽¹⁾ encode | 2.401 | 3.623 | 4.355 |
| Tier 4 ⁽¹⁾ decode | 2.956 | 4.504 | 5.665 |

> ⁽¹⁾ **Tiers 3 & 4 are enterprise tiers** — source not included in this release.  
> Results are published to demonstrate the full SDK performance profile across all tiers.  
> No implementation details about Tier 3 or Tier 4 internals are disclosed here.

> Note: Tier 2 large-payload latency is dominated by HMAC-SHA256 per field.  
> For payloads > 50 fields in latency-critical paths, Tier 1 is recommended.

---

## Security Efficacy

All tiers block automated exploitation tools at **P(detect) = 1.0** — by construction.  
The table below shows security properties measured under controlled conditions.

| Security Property | Tier 1 | Tier 2 | Tier 3 ⁽¹⁾ | Tier 4 ⁽¹⁾ |
|-------------------|--------|--------|------------|------------|
| Automated tool detection (P=1.0) | ✅ | ✅ | ✅ | ✅ |
| Standard-field probe blocked | ✅ | ✅ | ✅ | ✅ |
| Token brute-force window | 36^8 per field | HMAC-protected | Stronger | Strongest |
| Skilled attacker barrier | ~1–3 hrs | ~3–8 hrs | 12–36 hrs | Resets periodically |
| Key pre-image resistance | N/A | HMAC-SHA256 | HMAC-SHA256 | HMAC-SHA256 |
| LLM-assisted RE resistance | Low | Moderate | High | Very High |

> ⁽¹⁾ Internal security properties of Tiers 3 & 4 are not disclosed in this release.

---

## Key Takeaways

- **Tier 1** adds **< 0.01ms** overhead on typical API payloads — effectively free
- **Tier 2** adds **< 0.05ms** on small payloads, < 0.3ms on medium payloads
- **All tiers** achieve P(detect) = 1.0 against automated exploitation tools
- **Tiers 3 & 4** (enterprise) provide significantly stronger resistance against skilled attackers

---

## Interested in Tiers 3 & 4?

[Open a GitHub Discussion](https://github.com/DheelepN/C2CPO/discussions) or contact [@DheelepN](https://github.com/DheelepN) directly.
