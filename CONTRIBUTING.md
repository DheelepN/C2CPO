# Contributing to C2CPO

Thank you for considering a contribution to C2CPO! This project benefits enormously from community testing, bug reports, and improvements. Please take a moment to read these guidelines before opening an issue or pull request.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Report a Bug](#how-to-report-a-bug)
- [How to Suggest a Feature](#how-to-suggest-a-feature)
- [Development Setup](#development-setup)
- [Pull Request Workflow](#pull-request-workflow)
- [Test Requirements](#test-requirements)
- [Code Style](#code-style)
- [License & Attribution](#license--attribution)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this standard.

---

## How to Report a Bug

1. **Check existing issues** — search [GitHub Issues](https://github.com/DheelepN/C2CPO/issues) to see if it has already been reported.
2. **Use the bug report template** — click "New Issue" and select "Bug Report".
3. **Include the following information:**
   - SDK language (Python / Node.js) and version
   - Tier in use (1 or 2)
   - Python / Node.js version
   - Operating system
   - Minimal reproduction case
   - Expected vs actual behavior

> 🔒 **Security vulnerabilities must NOT be reported as public issues.** Use [GitHub Security Advisories](https://github.com/DheelepN/C2CPO/security/advisories/new). See [SECURITY.md](SECURITY.md).

---

## How to Suggest a Feature

1. Open a [GitHub Discussion](https://github.com/DheelepN/C2CPO/discussions) under the "Ideas" category.
2. Describe the use case, not just the feature — help us understand *why* it would be valuable.
3. If the idea gains traction, we'll convert it to a tracked issue.

---

## Development Setup

### Python SDK

```bash
git clone https://github.com/DheelepN/C2CPO.git
cd c2cpo

# Install in editable mode with dev dependencies
pip install -e "sdk/python[dev]"

# Run tests
python -m pytest sdk/python/tests/ -v
```

### Node.js SDK

```bash
cd sdk/nodejs

# Install dependencies
npm install

# Run tests
npm test

# TypeScript type-check
npx tsc --noEmit
```

### Running the Docker Demo

```bash
cd demo
docker compose up
```

---

## Pull Request Workflow

1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b fix/your-descriptive-branch-name
   ```

2. **Make your changes.** Follow the code style guidelines below.

3. **Add or update tests** — all pull requests must include tests that cover the changed behavior. See [Test Requirements](#test-requirements).

4. **Add a CHANGELOG entry** under an `[Unreleased]` heading in [CHANGELOG.md](CHANGELOG.md).

5. **Commit atomically** — one logical change per commit. Use a clear commit message:
   ```
   fix(tier2): correct base36 negative number handling
   ```

6. **Open the pull request** using the provided template. Fill in all checklist items before requesting review.

7. **CI must pass** — all tests across Python 3.10/3.11/3.12 and Node.js 18/20/22 must be green.

---

## Test Requirements

- **New features** must include tests in both Python (`sdk/python/tests/`) and Node.js (`sdk/nodejs/tests/`) if they affect both SDKs.
- **Bug fixes** must include a regression test that fails before the fix and passes after.
- **Cross-SDK behaviour changes** must update `tests/interop.test.ts` and the corresponding Python test to verify parity.
- Tests must pass the full CI matrix (see `.github/workflows/ci.yml`).

---

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Type annotations required for all public functions and methods
- Maximum line length: 120 characters
- No third-party dependencies in the core SDK (only the Python standard library)

### TypeScript / Node.js

- Follow the project's `tsconfig.json` (strict mode enabled)
- Use `async/await` over raw Promises
- No third-party production dependencies — only `devDependencies` for testing/typing
- All exported symbols must be typed explicitly

---

## License & Attribution

By contributing to this repository, you agree that your contributions will be licensed under the same [CC BY-NC 4.0 License](LICENSE) as the rest of the project.

**No CLA is required.** Your git commit authorship is your attribution.

If you build something with C2CPO and would like to be listed in the project acknowledgements, mention it in your pull request.

---

**Thank you for helping make C2CPO better!** 🛡️
