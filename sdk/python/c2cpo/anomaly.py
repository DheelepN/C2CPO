from datetime import datetime, timezone
import json
import hashlib
import sys
import threading
import urllib.request
import logging


class AnomalyDetector:
    """
    Emits structured violation events to stdout (and optionally a webhook).

    Every FORMAT_VIOLATION event is written as a single-line JSON object to
    stdout, making it trivially ingestible by any SIEM, log aggregator, or
    cloud logging pipeline (Splunk, Datadog, CloudWatch, etc.).

    Webhook delivery is fire-and-forget in a daemon thread, capped at 400ms
    to fit within the 500ms normative SLA.

    Example event::

        {
          "timestamp": "2026-04-30T07:22:00.000Z",
          "source_ip": "203.0.113.42",
          "endpoint_id": "payment-service",
          "violation_type": "FORMAT_VIOLATION",
          "severity": "HIGH",
          "failure_cause": "ATTACKER_PAYLOAD",
          "raw_request_hash": "sha256:...",
          "epoch_number": 0,
          "tier": 1
        }
    """

    def __init__(self, endpoint_id: str, tier: int = 1, webhook_url: str = None):
        """
        Args:
            endpoint_id: Service name included in every emitted event.
            tier:        C2CPO tier number (1 or 2 for the open-source release).
            webhook_url: Optional HTTP/HTTPS URL to POST events to asynchronously.
        """
        self.endpoint_id = endpoint_id
        self.tier = tier
        self.webhook_url = webhook_url

    def emit_violation(
        self,
        violation_type: str,
        severity: str,
        failure_cause: str,
        raw_request_hash: str,
        epoch_number: int,
        source_ip: str = "unknown",
    ):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            "source_ip": source_ip,
            "endpoint_id": self.endpoint_id,
            "violation_type": violation_type,
            "severity": severity,
            "failure_cause": failure_cause,
            "raw_request_hash": raw_request_hash,
            "epoch_number": epoch_number,
            "tier": self.tier,
        }

        event_str = json.dumps(event)
        print(event_str, file=sys.stdout, flush=True)

        if self.webhook_url:
            threading.Thread(
                target=self._send_webhook,
                args=(event_str,),
                daemon=True,
            ).start()

    def _send_webhook(self, payload_str: str):
        req = urllib.request.Request(
            self.webhook_url,
            data=payload_str.encode('utf-8'),
            headers={'Content-Type': 'application/json'},
        )
        try:
            urllib.request.urlopen(req, timeout=0.4)
        except Exception as e:
            logging.error(f"C2CPO webhook delivery failed: {e}")

    def log_format_violation(
        self,
        raw_request: str,
        epoch_number: int,
        source_ip: str = "unknown",
    ):
        """Emit a FORMAT_VIOLATION event (standard field detected in payload)."""
        req_hash = hashlib.sha256(raw_request.encode('utf-8')).hexdigest()
        self.emit_violation(
            violation_type="FORMAT_VIOLATION",
            severity="HIGH",
            failure_cause="ATTACKER_PAYLOAD",
            raw_request_hash=req_hash,
            epoch_number=epoch_number,
            source_ip=source_ip,
        )
