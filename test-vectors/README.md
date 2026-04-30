# C2CPO Test Vectors

Machine-readable normative test vectors for verifying cross-SDK interoperability.

Any SDK implementation that passes all vectors in both files produces identical encoded output to this reference implementation.

## Files

| File | Purpose |
|------|---------|
| `epoch_0_vectors.json` | Primary field mapping test vectors |
| `epoch_1_vectors.json` | Secondary field mapping test vectors |

## Schema

```json
{
  "schema_version": "1.0",
  "vectors": [
    {
      "standard_field": "amount",
      "obfuscated_token": "XR7F2K9Q"
    }
  ]
}
```

## CI Verification

The cross-SDK interoperability test verifies that both the Python and Node.js SDKs produce identical HMAC outputs and field mappings for the same inputs.

## Important

- `master_secret_hex` in the vector files is a **synthetic test key only** — it must **never** be used in production
- These vectors are normative — any implementation that fails them is not C2CPO-compliant
