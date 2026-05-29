# demo/producer/app.py
import urllib.request
import json
import time
import os
from c2cpo import Tier1, Tier2, KeyManager
CONSUMER_URL = os.environ.get("CONSUMER_URL", "http://localhost:8080")
tier1_encoder = Tier1("demo-producer")
try:
    secret = KeyManager().get_master_key()
    tier2_encoder = Tier2("demo-producer", master_secret=secret)
except Exception as e:
    print(f"Failed to initialize Tier 2 encoder: {e}")
    tier2_encoder = None


def send_request(payload: dict, description: str, endpoint: str = "/tier1"):
    print(f"\n{'─'*60}")
    print(f"  {description}")
    print(f"  Payload: {json.dumps(payload)}")
    print(f"{'─'*60}")

    req = urllib.request.Request(
        CONSUMER_URL + endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )

    try:
        response = urllib.request.urlopen(req)
        body = response.read().decode('utf-8')
        print(f"  ✓ STATUS 200: {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"  ✗ STATUS {e.code}: BLOCKED (as expected for attacker payload)")
    except Exception as e:
        print(f"  CONNECTION ERROR: {e}")


if __name__ == "__main__":
    print("\nC2CPO Demo — Tier 1: Field Name Obfuscation")
    print("Waiting for consumer to start...")
    time.sleep(3)

    standard_payload = {
        "amount": 1500,
        "user_id": "U123",
        "currency": "USD",
    }

    # 1. Standard REST request → BLOCKED (simulates automated exploitation tool)
    send_request(standard_payload, "STANDARD REST REQUEST (Tier 1) ← attacker / misconfigured producer", endpoint="/tier1")

    time.sleep(1)

    # 2. C2CPO-encoded request → SUCCEEDS
    encoded_payload = tier1_encoder.encode(standard_payload)
    send_request(encoded_payload, "C2CPO-ENCODED REQUEST (Tier 1) ← legitimate producer", endpoint="/tier1")

    if tier2_encoder:
        print("\nC2CPO Demo — Tier 2: Custom Value Encoding")
        time.sleep(1)

        # 3. Standard REST request → BLOCKED
        send_request(standard_payload, "STANDARD REST REQUEST (Tier 2) ← attacker / misconfigured producer", endpoint="/tier2")
        
        time.sleep(1)
        
        # 4. C2CPO-encoded request → SUCCEEDS
        encoded_payload_tier2 = tier2_encoder.encode(standard_payload)
        send_request(encoded_payload_tier2, "C2CPO-ENCODED REQUEST (Tier 2) ← legitimate producer", endpoint="/tier2")

    print("\nDemo complete.\n")
