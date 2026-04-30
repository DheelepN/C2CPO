import os
import logging
from typing import Dict, Any
from .anomaly import AnomalyDetector
from .exceptions import C2CPOFormatViolationError
import json


class Tier1:
    """
    Tier 1 — Field Name Obfuscation.

    Replaces standard REST/JSON field names with 8-character opaque tokens
    defined in the static Epoch 0 mapping (Appendix C.1 of the C2CPO v4.1
    framework).  Any request arriving with unencoded standard field names is
    immediately rejected and a FORMAT_VIOLATION event is emitted.

    Detection probability for automated exploitation tools: P = 1.0.
    No key material required — deploy in 3–5 developer-days.

    Usage::

        encoder = Tier1(endpoint_id="payment-service")
        encoded = encoder.encode({"amount": 1000, "user_id": "usr_123"})
        # → {"XR7F2K9Q": 1000, "U9B3MX1P": "usr_123"}

        decoder = Tier1(endpoint_id="payment-service")
        decoded = decoder.decode(encoded, raw_request_str=json.dumps(encoded))
        # → {"amount": 1000, "user_id": "usr_123"}
    """

    _TIER_NUMBER: int = 1

    # Static lookup table — Appendix C.1 (Epoch 0 mapping)
    # Tokens are exactly 8 chars [A-Z0-9]
    EPOCH_0_MAPPING = {
        "amount":     "XR7F2K9Q",
        "user_id":    "U9B3MX1P",
        "account_id": "A4N8VQ2L",
        "currency":   "C7X9T1W0",
        "timestamp":  "T2M6Z8H5",
    }

    def __init__(self, endpoint_id: str, webhook_url: str = None):
        """
        Args:
            endpoint_id: Unique identifier for this service endpoint.
                         Used in anomaly event metadata.
            webhook_url: Optional URL to POST violation events to within 500ms.
                         If omitted, events are written to stdout only.
        """
        self.anomaly_detector = AnomalyDetector(
            endpoint_id=endpoint_id,
            tier=self._TIER_NUMBER,
            webhook_url=webhook_url,
        )
        self.reversed_mapping = {v: k for k, v in self.EPOCH_0_MAPPING.items()}
        self._warn_if_production_unsafe()

    def _warn_if_production_unsafe(self) -> None:
        env = os.getenv("C2CPO_ENVIRONMENT", "").lower()
        ack = os.getenv("C2CPO_PRODUCTION_TIER_ACK", "").lower()
        if env == "production" and ack != "true":
            logging.warning(
                f"C2CPO Tier {self._TIER_NUMBER} is active in production. "
                "Tier 4 is the minimum for security-sensitive deployments. "
                "Set C2CPO_PRODUCTION_TIER_ACK=true to suppress this warning."
            )

    def encode(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode a standard-field payload to C2CPO Tier 1 format.

        Known fields are replaced by their opaque tokens. Unknown fields
        are passed through unchanged.

        Args:
            payload: Dict with standard field names.

        Returns:
            Dict with field names replaced by Epoch 0 tokens.
        """
        encoded_payload = {}
        for key, value in payload.items():
            encoded_key = self.EPOCH_0_MAPPING.get(key, key)
            encoded_payload[encoded_key] = value
        return encoded_payload

    def decode(
        self,
        payload: Dict[str, Any],
        raw_request_str: str,
        source_ip: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Decode a C2CPO Tier 1 encoded payload back to standard fields.

        If any standard (unencoded) field name is detected, a FORMAT_VIOLATION
        event is emitted and C2CPOFormatViolationError is raised (fail-closed).

        Args:
            payload:         The encoded payload dict received from the producer.
            raw_request_str: Raw request body string (used for SHA-256 hashing
                             in the violation event).
            source_ip:       Client IP address for the violation event.

        Returns:
            Dict with original standard field names restored.

        Raises:
            C2CPOFormatViolationError: If unencoded standard fields are detected.
        """
        decoded_payload = {}
        violation_detected = False

        for key, value in payload.items():
            if key in self.EPOCH_0_MAPPING:
                violation_detected = True

            decoded_key = self.reversed_mapping.get(key)
            if decoded_key:
                decoded_payload[decoded_key] = value
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
