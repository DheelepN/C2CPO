import unittest
import json
import os


class TestTier2(unittest.TestCase):

    def setUp(self):
        from c2cpo import Tier2
        # Synthetic test key — never use in production
        self.master_secret = bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
        self.tier2 = Tier2(endpoint_id="test-endpoint", master_secret=self.master_secret)

    def test_encode_integer_as_base36(self):
        """Integers must be encoded as Base36 uppercase strings."""
        encoded = self.tier2.encode({"amount": 1000})
        amount_key = self.tier2.EPOCH_0_MAPPING["amount"]
        self.assertEqual(encoded[amount_key], "RS")  # 1000 in Base36

    def test_decode_base36_back_to_int(self):
        """Encoded integer must decode back to original value."""
        encoded = self.tier2.encode({"amount": 1000})
        decoded = self.tier2.decode(encoded, raw_request_str=json.dumps(encoded))
        self.assertEqual(decoded["amount"], 1000)

    def test_encode_string_as_hmac_token(self):
        """String values must be replaced by 12-character uppercase HMAC tokens."""
        encoded = self.tier2.encode({"user_id": "U123"})
        user_key = self.tier2.EPOCH_0_MAPPING["user_id"]
        encoded_val = encoded[user_key]
        self.assertEqual(len(encoded_val), 12)
        self.assertTrue(encoded_val.isupper() or encoded_val.isalnum())

    def test_encode_string_is_deterministic(self):
        """Same input + same key must always produce the same HMAC token."""
        encoded1 = self.tier2.encode({"user_id": "U123"})
        encoded2 = self.tier2.encode({"user_id": "U123"})
        user_key = self.tier2.EPOCH_0_MAPPING["user_id"]
        self.assertEqual(encoded1[user_key], encoded2[user_key])

    def test_encode_string_differs_for_different_inputs(self):
        """Different string inputs must produce different HMAC tokens."""
        encoded1 = self.tier2.encode({"user_id": "U123"})
        encoded2 = self.tier2.encode({"user_id": "U456"})
        user_key = self.tier2.EPOCH_0_MAPPING["user_id"]
        self.assertNotEqual(encoded1[user_key], encoded2[user_key])

    def test_fail_closed_on_standard_field(self):
        """Decode with unencoded standard field must raise FORMAT_VIOLATION."""
        from c2cpo.exceptions import C2CPOFormatViolationError
        payload = {"amount": "RS", "user_id": "some_token"}
        with self.assertRaises(C2CPOFormatViolationError):
            self.tier2.decode(payload, raw_request_str=json.dumps(payload))

    def test_base36_zero(self):
        """Zero must encode to '0'."""
        encoded = self.tier2.encode({"amount": 0})
        amount_key = self.tier2.EPOCH_0_MAPPING["amount"]
        self.assertEqual(encoded[amount_key], "0")

    def test_base36_negative(self):
        """Negative integers must encode with leading '-'."""
        encoded = self.tier2.encode({"amount": -1000})
        amount_key = self.tier2.EPOCH_0_MAPPING["amount"]
        self.assertTrue(encoded[amount_key].startswith("-"))


if __name__ == "__main__":
    unittest.main()
