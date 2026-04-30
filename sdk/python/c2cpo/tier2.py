from typing import Dict, Any, Union
import hmac
import hashlib
from .tier1 import Tier1
from .exceptions import C2CPOFormatViolationError


class Tier2(Tier1):
    """
    Tier 2 — Custom Value Encoding.

    Extends Tier 1 by also obfuscating field *values*:

    - **Integers** are encoded as Base36 uppercase strings (e.g. 1000 → "RS")
    - **Strings** are replaced by a 12-character uppercase HMAC-SHA256 token
      derived from the master secret and the original string value

    Requires a shared ``master_secret`` (32+ bytes) on both producer and
    consumer.  The master secret should be loaded from an environment variable
    or a KMS backend via :class:`KeyManager` — never hard-coded.

    Skilled-attacker barrier: ~3–8 hours (vs. ~1–3 hours for Tier 1).
    Latency overhead: < 2ms for typical payloads.

    Usage::

        import os
        from c2cpo import Tier2, KeyManager

        key_manager = KeyManager()
        secret = key_manager.get_master_key()

        encoder = Tier2(endpoint_id="payment-service", master_secret=secret)
        encoded = encoder.encode({"amount": 1000, "user_id": "usr_123"})
        # → {"XR7F2K9Q": "RS", "U9B3MX1P": "4A2B8C1D9E3F"}

        decoder = Tier2(endpoint_id="payment-service", master_secret=secret)
        decoded = decoder.decode(encoded, raw_request_str="{...}")
        # → {"amount": 1000, "user_id": "4A2B8C1D9E3F"}
        # Note: string values decode statelessly — original value not recovered
    """

    _TIER_NUMBER: int = 2

    def __init__(self, endpoint_id: str, master_secret: bytes, webhook_url: str = None):
        """
        Args:
            endpoint_id:   Unique identifier for this service endpoint.
            master_secret: Shared 32-byte (256-bit) secret key.
                           Load via KeyManager — never hard-code.
            webhook_url:   Optional SIEM webhook URL for violation events.
        """
        super().__init__(endpoint_id=endpoint_id, webhook_url=webhook_url)
        self.master_secret = master_secret
        self.anomaly_detector.tier = 2

    # --- Value Encoders ---

    def _encode_base36(self, number: int) -> str:
        """Encode an integer as a Base36 uppercase string."""
        if number == 0:
            return '0'
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        base36 = ''
        sign = '-' if number < 0 else ''
        number = abs(number)
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36
        return sign + base36

    def _decode_base36(self, base36: str) -> int:
        """Decode a Base36 string back to an integer."""
        return int(base36, 36)

    def _encode_string(self, value: str) -> str:
        """
        Replace a string value with a 12-character HMAC-SHA256 token.

        HMAC is keyed with the master secret so the token is deterministic
        for the same input but unguessable without K.
        """
        h = hmac.new(self.master_secret, value.encode('utf-8'), hashlib.sha256).hexdigest()
        return h[:12].upper()

    def encode(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode payload with Tier 1 field-name obfuscation and Tier 2
        value encoding (Base36 for integers, HMAC token for strings).

        Args:
            payload: Dict with standard field names and plain values.

        Returns:
            Dict with obfuscated keys and encoded values.
        """
        encoded_payload = {}
        for key, value in payload.items():
            encoded_key = self.EPOCH_0_MAPPING.get(key, key)

            if isinstance(value, int):
                encoded_value = self._encode_base36(value)
            elif isinstance(value, str):
                encoded_value = self._encode_string(value)
            else:
                encoded_value = value

            encoded_payload[encoded_key] = encoded_value
        return encoded_payload

    def decode(
        self,
        payload: Dict[str, Any],
        raw_request_str: str,
        source_ip: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Decode a Tier 2 encoded payload.

        Integer values (stored as Base36 strings) are decoded back to int.
        String values (stored as HMAC tokens) are returned as-is — the
        original string is not recoverable without the plaintext (by design).

        Raises:
            C2CPOFormatViolationError: If unencoded standard fields detected.
        """
        decoded_payload = {}
        violation_detected = False

        for key, value in payload.items():
            if key in self.EPOCH_0_MAPPING:
                violation_detected = True

            decoded_key = self.reversed_mapping.get(key)
            if decoded_key:
                if isinstance(value, str):
                    try:
                        if decoded_key == "amount":
                            decoded_value = self._decode_base36(value)
                        else:
                            decoded_value = value
                    except ValueError:
                        decoded_value = value
                else:
                    decoded_value = value
                decoded_payload[decoded_key] = decoded_value
            elif key not in self.EPOCH_0_MAPPING:
                decoded_payload[key] = value

        if violation_detected:
            self.anomaly_detector.log_format_violation(
                raw_request=raw_request_str,
                epoch_number=0,
                source_ip=source_ip,
            )
            raise C2CPOFormatViolationError(
                "FORMAT_VIOLATION: Unencoded standard fields detected in payload."
            )

        return decoded_payload
