import os
import urllib.request
import json
import logging
from typing import Optional


class C2CPOKeyUnavailableError(Exception):
    """
    Raised when the master secret cannot be retrieved from any backend.

    C2CPO fails closed — if the key is unavailable, the encoder/decoder
    will not operate, preventing silent fallback to unprotected communication.
    """
    pass


class KeyManager:
    """
    Retrieves the C2CPO master secret from a configured backend.

    Supported backends (in priority order):

    1. **HashiCorp Vault** — set ``use_vault=True``, ``VAULT_ADDR``, ``VAULT_TOKEN``
    2. **Cloud KMS** — set ``C2CPO_KMS_BACKEND`` to ``AWS``, ``AZURE``, or ``GCP``
    3. **Environment variable** — set ``C2CPO_MASTER_SECRET`` (hex string, 64+ chars)

    The master secret is **never logged** at any level. Exceptions are wrapped
    to prevent accidental key material leakage in stack traces.

    Usage::

        # Simplest — environment variable
        export C2CPO_MASTER_SECRET="your-64-char-hex-string"

        key_manager = KeyManager()
        secret = key_manager.get_master_key()  # Returns bytes

        # HashiCorp Vault
        key_manager = KeyManager(use_vault=True)
        secret = key_manager.get_master_key()
    """

    def __init__(self, use_vault: bool = False):
        self.use_vault = use_vault
        self.vault_addr = os.getenv("VAULT_ADDR")
        self.vault_token = os.getenv("VAULT_TOKEN")

    def get_master_key(self) -> bytes:
        """
        Retrieve and return the master secret as bytes.

        Fails closed (raises C2CPOKeyUnavailableError) if the secret
        is unavailable from all configured backends.

        Returns:
            Master secret as bytes (minimum 32 bytes recommended).

        Raises:
            C2CPOKeyUnavailableError: If the secret cannot be retrieved.
        """
        try:
            if self.use_vault:
                key_hex = self._get_from_vault()
            elif os.getenv("C2CPO_KMS_BACKEND"):
                key_hex = self._get_from_cloud_kms()
            else:
                key_hex = os.getenv("C2CPO_MASTER_SECRET")

            if not key_hex:
                raise C2CPOKeyUnavailableError(
                    "Master secret not found in any configured backend. "
                    "Set C2CPO_MASTER_SECRET, VAULT_ADDR+VAULT_TOKEN, or C2CPO_KMS_BACKEND."
                )

            b_key = bytes.fromhex(key_hex)
            if len(b_key) < 32:
                logging.warning(
                    "C2CPO master secret is less than 32 bytes (256 bits). "
                    "Use a 64-character hex string (32 bytes) or longer for production."
                )
            return b_key

        except Exception as e:
            if isinstance(e, C2CPOKeyUnavailableError):
                raise
            raise C2CPOKeyUnavailableError(
                "Backend retrieval failed. Check logs for details."
            ) from e

    def _get_from_cloud_kms(self) -> Optional[str]:
        backend = os.getenv("C2CPO_KMS_BACKEND")

        if backend == "AWS":
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError
            try:
                kms = boto3.client('kms')
                logging.info("Calling AWS KMS for C2CPO master secret.")
                return os.getenv("MOCK_AWS_KMS_RESPONSE")  # Replace with real KMS call
            except (BotoCoreError, ClientError) as e:
                raise C2CPOKeyUnavailableError("AWS KMS communication failed.") from e

        elif backend == "AZURE":
            logging.info("Retrieving from Azure Key Vault.")
            return os.getenv("MOCK_AZURE_KV_RESPONSE")  # Replace with real SDK call

        elif backend == "GCP":
            logging.info("Retrieving from GCP KMS.")
            return os.getenv("MOCK_GCP_KMS_RESPONSE")  # Replace with real SDK call

        return None

    def _get_from_vault(self) -> Optional[str]:
        if not self.vault_addr or not self.vault_token:
            raise C2CPOKeyUnavailableError(
                "VAULT_ADDR or VAULT_TOKEN not set in environment."
            )

        req = urllib.request.Request(
            f"{self.vault_addr}/v1/secret/c2cpo/master_key",
            headers={"X-Vault-Token": self.vault_token},
        )
        try:
            with urllib.request.urlopen(req, timeout=3.0) as response:
                body = json.loads(response.read().decode('utf-8'))
                return body.get("data", {}).get("key")
        except Exception as e:
            raise C2CPOKeyUnavailableError("Vault communication failed.") from e
