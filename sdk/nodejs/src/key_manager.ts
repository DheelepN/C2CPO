import * as http from 'http';
import * as https from 'https';

/**
 * Raised when the master secret cannot be retrieved from any backend.
 * C2CPO fails closed — if the key is unavailable, the encoder will not operate.
 */
export class C2CPOKeyUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'C2CPOKeyUnavailableError';
  }
}

/**
 * Retrieves the C2CPO master secret from a configured backend.
 *
 * Supported backends (in priority order):
 * 1. **HashiCorp Vault** — set `useVault=true`, `VAULT_ADDR`, `VAULT_TOKEN`
 * 2. **Cloud KMS** — set `C2CPO_KMS_BACKEND` to `AWS`, `AZURE`, or `GCP`
 * 3. **Environment variable** — set `C2CPO_MASTER_SECRET` (hex string, 64+ chars)
 *
 * @example
 * ```typescript
 * // Simplest — environment variable
 * process.env.C2CPO_MASTER_SECRET = 'your-64-char-hex-string';
 * const secret = await new KeyManager().getMasterKey();
 *
 * // HashiCorp Vault
 * const secret = await new KeyManager(true).getMasterKey();
 * ```
 */
export class KeyManager {
  private useVault: boolean;
  private vaultAddr?: string;
  private vaultToken?: string;

  constructor(useVault: boolean = false) {
    this.useVault = useVault;
    this.vaultAddr = process.env.VAULT_ADDR;
    this.vaultToken = process.env.VAULT_TOKEN;
  }

  public async getMasterKey(): Promise<Buffer> {
    try {
      let keyHex: string | undefined;

      if (this.useVault) {
        keyHex = await this.getFromVault();
      } else if (process.env.C2CPO_KMS_BACKEND) {
        keyHex = await this.getFromCloudKms();
      } else {
        keyHex = process.env.C2CPO_MASTER_SECRET;
      }

      if (!keyHex) {
        throw new C2CPOKeyUnavailableError(
          'Master secret not found. Set C2CPO_MASTER_SECRET, VAULT_ADDR+VAULT_TOKEN, or C2CPO_KMS_BACKEND.'
        );
      }

      const bKey = Buffer.from(keyHex, 'hex');
      if (bKey.length < 32) {
        console.warn('C2CPO master secret is less than 32 bytes. Use a 64-char hex string for production.');
      }
      return bKey;
    } catch (e) {
      if (e instanceof C2CPOKeyUnavailableError) throw e;
      throw new C2CPOKeyUnavailableError(`Backend retrieval failed: ${e}`);
    }
  }

  private async getFromCloudKms(): Promise<string | undefined> {
    const backend = process.env.C2CPO_KMS_BACKEND;
    if (backend === 'AWS') {
      console.log('Calling AWS KMS for C2CPO master secret.');
      return process.env.MOCK_AWS_KMS_RESPONSE; // Replace with real AWS SDK call
    } else if (backend === 'AZURE') {
      console.log('Retrieving from Azure Key Vault.');
      return process.env.MOCK_AZURE_KV_RESPONSE; // Replace with real Azure SDK call
    } else if (backend === 'GCP') {
      console.log('Retrieving from GCP KMS.');
      return process.env.MOCK_GCP_KMS_RESPONSE; // Replace with real GCP SDK call
    }
    return undefined;
  }

  private async getFromVault(): Promise<string | undefined> {
    if (!this.vaultAddr || !this.vaultToken) {
      throw new C2CPOKeyUnavailableError('VAULT_ADDR or VAULT_TOKEN not set in environment.');
    }

    return new Promise((resolve, reject) => {
      const url = new URL(`${this.vaultAddr}/v1/secret/c2cpo/master_key`);
      const client = url.protocol === 'https:' ? https : http;

      const req = client.request(url, {
        method: 'GET',
        headers: { 'X-Vault-Token': this.vaultToken },
        timeout: 3000,
      }, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
          try {
            const body = JSON.parse(data);
            resolve(body?.data?.key);
          } catch (err) {
            reject(err);
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Vault request timeout')); });
      req.end();
    });
  }
}
