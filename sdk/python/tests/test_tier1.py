import unittest
import json
import os


class TestTier1(unittest.TestCase):

    def setUp(self):
        from c2cpo import Tier1
        self.tier1 = Tier1(endpoint_id="test-endpoint")
        vectors_path = os.path.join(
            os.path.dirname(__file__), "../../../test-vectors/epoch_0_vectors.json"
        )
        with open(vectors_path, 'r') as f:
            self.epoch_0_vectors = json.load(f)

    def test_encode_replaces_standard_fields(self):
        """Encoded payload must not contain any standard field names."""
        test_payload = {v["standard_field"]: "value" for v in self.epoch_0_vectors["vectors"]}
        encoded = self.tier1.encode(test_payload)
        for vector in self.epoch_0_vectors["vectors"]:
            self.assertIn(vector["obfuscated_token"], encoded)
            self.assertNotIn(vector["standard_field"], encoded)

    def test_encode_decode_roundtrip(self):
        """Encode then decode must recover the original payload exactly."""
        test_payload = {v["standard_field"]: "test_value" for v in self.epoch_0_vectors["vectors"]}
        encoded = self.tier1.encode(test_payload)
        decoded = self.tier1.decode(encoded, raw_request_str=json.dumps(encoded))
        self.assertEqual(test_payload, decoded)

    def test_unknown_fields_pass_through(self):
        """Fields not in the mapping must be forwarded unchanged."""
        payload = {"custom_field": "custom_value"}
        encoded = self.tier1.encode(payload)
        self.assertEqual(encoded["custom_field"], "custom_value")

    def test_fail_closed_on_standard_field(self):
        """Decode with unencoded standard field must raise FORMAT_VIOLATION."""
        from c2cpo.exceptions import C2CPOFormatViolationError
        payload_with_violation = {"amount": 100, "user_id": "U123"}
        with self.assertRaises(C2CPOFormatViolationError):
            self.tier1.decode(
                payload_with_violation,
                raw_request_str=json.dumps(payload_with_violation),
            )

    def test_encode_multiple_types(self):
        """Encode should handle int, str, float, None values."""
        payload = {"amount": 1000, "currency": "USD"}
        encoded = self.tier1.encode(payload)
        self.assertIn("XR7F2K9Q", encoded)
        self.assertIn("C7X9T1W0", encoded)
        self.assertEqual(encoded["XR7F2K9Q"], 1000)
        self.assertEqual(encoded["C7X9T1W0"], "USD")


if __name__ == "__main__":
    unittest.main()
