# Changelog

All notable changes to the C2CPO SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-04-30

### Added

#### Tier 1 — Field Name Obfuscation
- Static field name mapping encoder/decoder (Python 3.10+ and Node.js 18+)
- Anomaly Detector with `FORMAT_VIOLATION` events to stdout and optional webhook
- Test vectors for epoch 0 and epoch 1 (Appendix C schema)
- Docker demo: standard REST request blocked (HTTP 400), C2CPO request succeeds (HTTP 200)
- Production-unsafe warning when deploying without explicit `C2CPO_PRODUCTION_TIER_ACK=true`

#### Tier 2 — Custom Value Encoding
- Base36 numeric encoding/decoding
- HMAC-SHA256 truncated string tokens (12 uppercase hex characters)
- Key Manager with environment variable, HashiCorp Vault, AWS KMS, Azure Key Vault, and GCP KMS backends
- Cross-SDK interoperability tests confirming Python ↔ Node.js HMAC parity

#### Documentation
- README with honesty requirements, tier selection guide, and quick-start examples
- Integration guide (Tier 1 and Tier 2)
- Threat model
- Contributing guidelines and Code of Conduct
- Security policy with safe harbour clause

#### CI/CD
- GitHub Actions CI pipeline (Python 3.10/3.11/3.12 + Node.js 18/20/22)
- Cross-SDK interoperability verification in CI
- Secret leakage scan in CI

### Security
- Fail-closed on encoder crash or key unavailability
- Master secret never stored in application logs, stack traces, or error messages
- Production-tier warning when Tiers 1–2 are active without explicit acknowledgment
