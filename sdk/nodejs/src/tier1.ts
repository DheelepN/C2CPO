import { AnomalyDetector } from './anomaly';
import { C2CPOFormatViolationError } from './exceptions';

/**
 * Tier 1 — Field Name Obfuscation.
 *
 * Replaces standard REST/JSON field names with 8-character opaque tokens
 * defined in the static Epoch 0 mapping (Appendix C.1 of the C2CPO v4.1
 * framework). Any request arriving with unencoded standard field names is
 * immediately rejected and a FORMAT_VIOLATION event is emitted.
 *
 * Detection probability for automated exploitation tools: P = 1.0.
 * No key material required — deploy in 3–5 developer-days.
 *
 * @example
 * ```typescript
 * const encoder = new Tier1('payment-service');
 * const encoded = encoder.encode({ amount: 1000, user_id: 'usr_123' });
 * // → { XR7F2K9Q: 1000, U9B3MX1P: 'usr_123' }
 *
 * const decoder = new Tier1('payment-service');
 * const decoded = decoder.decode(encoded, JSON.stringify(encoded));
 * // → { amount: 1000, user_id: 'usr_123' }
 * ```
 */
export class Tier1 {
  public anomalyDetector: AnomalyDetector;

  /** Epoch 0 static field mapping — Appendix C.1 */
  public static readonly EPOCH_0_MAPPING: Record<string, string> = {
    "amount":     "XR7F2K9Q",
    "user_id":    "U9B3MX1P",
    "account_id": "A4N8VQ2L",
    "currency":   "C7X9T1W0",
    "timestamp":  "T2M6Z8H5",
  };

  public reversedMapping: Record<string, string>;

  protected get productionSafe(): boolean { return false; }
  protected get tierNumber(): number { return 1; }

  /**
   * @param endpointId  Unique service endpoint identifier (used in anomaly events).
   * @param webhookUrl  Optional SIEM webhook URL for violation events.
   */
  constructor(endpointId: string, webhookUrl?: string) {
    this.anomalyDetector = new AnomalyDetector(endpointId, 1, webhookUrl);
    this.reversedMapping = {};
    for (const [key, value] of Object.entries(Tier1.EPOCH_0_MAPPING)) {
      this.reversedMapping[value] = key;
    }
    this._warnIfProductionUnsafe();
  }

  private _warnIfProductionUnsafe(): void {
    if (this.productionSafe) return;
    const env = (process.env.C2CPO_ENVIRONMENT || '').toLowerCase();
    const ack = (process.env.C2CPO_PRODUCTION_TIER_ACK || '').toLowerCase();
    if (env === 'production' && ack !== 'true') {
      console.warn(
        `C2CPO Tier ${this.tierNumber} is active in production. ` +
        'Tier 4 is the minimum for security-sensitive deployments. ' +
        'Set C2CPO_PRODUCTION_TIER_ACK=true to suppress this warning.'
      );
    }
  }

  /**
   * Encode a standard-field payload to C2CPO Tier 1 format.
   * Unknown fields are passed through unchanged.
   */
  public encode(payload: Record<string, any>): Record<string, any> {
    const encodedPayload: Record<string, any> = {};
    for (const [key, value] of Object.entries(payload)) {
      const encodedKey = Tier1.EPOCH_0_MAPPING[key] || key;
      encodedPayload[encodedKey] = value;
    }
    return encodedPayload;
  }

  /**
   * Decode a C2CPO Tier 1 encoded payload back to standard fields.
   * Fails closed — raises C2CPOFormatViolationError if standard fields detected.
   *
   * @param payload        Encoded payload dict from the producer.
   * @param rawRequestStr  Raw request body string (for SHA-256 hashing in events).
   * @param sourceIp       Client IP for the violation event.
   */
  public decode(
    payload: Record<string, any>,
    rawRequestStr: string,
    sourceIp: string = 'unknown'
  ): Record<string, any> {
    const decodedPayload: Record<string, any> = {};
    let violationDetected = false;

    for (const [key, value] of Object.entries(payload)) {
      if (key in Tier1.EPOCH_0_MAPPING) {
        violationDetected = true;
      }

      const decodedKey = this.reversedMapping[key];
      if (decodedKey) {
        decodedPayload[decodedKey] = value;
      } else if (!(key in Tier1.EPOCH_0_MAPPING)) {
        decodedPayload[key] = value;
      }
    }

    if (violationDetected) {
      this.anomalyDetector.logFormatViolation(rawRequestStr, 0, sourceIp);
      throw new C2CPOFormatViolationError(
        'FORMAT_VIOLATION: Unencoded standard fields detected in payload.'
      );
    }

    return decodedPayload;
  }
}
