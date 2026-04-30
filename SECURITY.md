# Security Policy

## Reporting a Vulnerability

**Preferred channel:** [GitHub Security Advisories](https://github.com/DheelepN/C2CPO/security/advisories/new)

If you prefer encrypted communication, use the maintainer's PGP key (published in this repository) or GitHub's built-in encrypted reporting mechanism.

**Do NOT open a public GitHub issue for security vulnerabilities.**

**Maintainer:** N Dheelep Sai Gupthaa

## Response SLA

| Severity | Acknowledgment | Patch or Advisory |
|----------|---------------|-------------------|
| CRITICAL | Within 48 hours | Within 30 days |
| HIGH | Within 48 hours | Within 30 days |
| MEDIUM | Within 48 hours | Within 90 days |
| LOW | Within 48 hours | Within 90 days |

## Scope

### In Scope

- SDK source code (Python and Node.js implementations — Tier 1 and Tier 2)
- Test vectors (`test-vectors/`)
- CI/CD pipeline configuration
- Normative documentation (integration guide, threat model)
- Key Manager backends (environment variable, Vault, AWS KMS, Azure Key Vault, GCP KMS)

### Out of Scope

- Theoretical claims in the C2CPO v4.1 framework paper (research claims, not software bugs)
- Deployed instances of C2CPO not maintained by this project
- Third-party integrations or forks
- Denial of service against ancillary detection mechanisms (known operational consideration, not a vulnerability)

## Disclosure Guidelines

1. **Do not** open a public GitHub issue for security vulnerabilities
2. **Do** use GitHub Security Advisories or the maintainer's PGP key
3. **Do** provide a clear description of the vulnerability, including:
   - Affected component (encoder, decoder, key manager, etc.)
   - Steps to reproduce
   - Impact assessment (confidentiality, integrity, availability)
   - Suggested fix if available
4. **Do not** include production key material (K, K_epoch) in any report

## Safe Harbour

Good-faith security research conducted in accordance with this policy will not result in legal action from the maintainers. We consider security research and vulnerability disclosure activities conducted consistent with this policy to be:

- Authorised under applicable anti-hacking laws
- Exempt from DMCA restrictions on circumvention
- Carried out for the benefit of the project and its users

We will not pursue legal action against researchers who:

- Act in good faith to avoid privacy violations, data destruction, and service disruption
- Only interact with test environments or their own deployments
- Report vulnerabilities through the channels described above
- Allow reasonable time for remediation before public disclosure

## Supply Chain Security

The C2CPO SDK is a high-value attack target in any deployment. A compromised SDK silently defeats all tiers simultaneously. We implement:

- **Signed releases** — all SDK distributions are cryptographically signed
- **Reproducible builds** — independent verification that distributed artifacts match clean builds from published source
- **No secrets in source** — K must never appear in source code, config files, or logs
