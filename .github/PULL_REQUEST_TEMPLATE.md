## Summary

<!-- Describe what this PR changes and why. Link to the issue it resolves if applicable. -->

Fixes # (issue)

## Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update
- [ ] CI / tooling change

## Checklist

- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] My code follows the project's style guidelines (PEP 8 / strict TypeScript)
- [ ] I have added tests that cover my change
- [ ] All existing tests pass locally (`pytest` and `npm test`)
- [ ] I have updated documentation if necessary
- [ ] I have added a `CHANGELOG.md` entry under `[Unreleased]`
- [ ] No secrets, API keys, or key material appear in any changed file
- [ ] Cross-SDK parity maintained (if change affects encode/decode logic, both Python and Node.js are updated)

## Testing Evidence

<!-- Paste test output or describe how you verified the change works. -->

```
$ python -m pytest sdk/python/tests/ -v
...
PASSED sdk/python/tests/test_tier1.py::TestTier1::test_encode_decode_roundtrip
PASSED sdk/python/tests/test_tier2.py::TestTier2::test_encode_base36
```
