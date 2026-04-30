import * as crypto from 'crypto';
import * as http from 'http';
import * as https from 'https';

/**
 * Emits structured violation events to stdout and optionally a webhook.
 *
 * Events are written as single-line JSON — ingestible by any SIEM,
 * log aggregator, or cloud logging pipeline (Splunk, Datadog, CloudWatch).
 *
 * Webhook delivery is fire-and-forget, capped at 400ms to fit the 500ms SLA.
 *
 * @example
 * ```json
 * {
 *   "timestamp": "2026-04-30T07:22:00.000Z",
 *   "source_ip": "203.0.113.42",
 *   "endpoint_id": "payment-service",
 *   "violation_type": "FORMAT_VIOLATION",
 *   "severity": "HIGH",
 *   "failure_cause": "ATTACKER_PAYLOAD",
 *   "raw_request_hash": "sha256:...",
 *   "epoch_number": 0,
 *   "tier": 1
 * }
 * ```
 */
export class AnomalyDetector {
  private endpointId: string;
  public tier: number;
  private webhookUrl?: string;

  constructor(endpointId: string, tier: number = 1, webhookUrl?: string) {
    this.endpointId = endpointId;
    this.tier = tier;
    this.webhookUrl = webhookUrl;
  }

  public emitViolation(
    violationType: string,
    severity: string,
    failureCause: string,
    rawRequestHash: string,
    epochNumber: number,
    sourceIp: string = 'unknown'
  ): void {
    const event = {
      timestamp: new Date().toISOString(),
      source_ip: sourceIp,
      endpoint_id: this.endpointId,
      violation_type: violationType,
      severity,
      failure_cause: failureCause,
      raw_request_hash: rawRequestHash,
      epoch_number: epochNumber,
      tier: this.tier,
    };

    const eventStr = JSON.stringify(event);
    process.stdout.write(eventStr + '\n');

    if (this.webhookUrl) {
      this.sendWebhook(eventStr);
    }
  }

  private sendWebhook(payloadStr: string): void {
    try {
      const url = new URL(this.webhookUrl!);
      const client = url.protocol === 'https:' ? https : http;

      const req = client.request(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payloadStr),
        },
        timeout: 400,
      });

      req.on('error', (e) => console.error(`C2CPO webhook delivery failed: ${e.message}`));
      req.on('timeout', () => req.destroy());
      req.write(payloadStr);
      req.end();
    } catch (e) {
      console.error(`C2CPO invalid webhook URL: ${e}`);
    }
  }

  public logFormatViolation(
    rawRequest: string,
    epochNumber: number,
    sourceIp: string = 'unknown'
  ): void {
    const reqHash = crypto.createHash('sha256').update(rawRequest, 'utf8').digest('hex');
    this.emitViolation(
      'FORMAT_VIOLATION',
      'HIGH',
      'ATTACKER_PAYLOAD',
      reqHash,
      epochNumber,
      sourceIp
    );
  }
}
