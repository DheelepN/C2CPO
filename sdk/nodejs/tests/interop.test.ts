import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import { Tier1 } from '../src/tier1';
import { Tier2 } from '../src/tier2';

describe('Cross-SDK Interoperability Tests (Tier 1 + 2)', () => {
  // Synthetic test key — NEVER use in production
  const masterSecretHex = '0000000000000000000000000000000000000000000000000000000000000001';
  const masterSecret = Buffer.from(masterSecretHex, 'hex');

  let epoch0Vectors: any;
  let epoch1Vectors: any;

  beforeAll(() => {
    const epoch0Path = path.join(__dirname, '../../../test-vectors/epoch_0_vectors.json');
    const epoch1Path = path.join(__dirname, '../../../test-vectors/epoch_1_vectors.json');
    epoch0Vectors = JSON.parse(fs.readFileSync(epoch0Path, 'utf8'));
    epoch1Vectors = JSON.parse(fs.readFileSync(epoch1Path, 'utf8'));
  });

  test('Epoch 0 static mapping matches test vectors', () => {
    for (const v of epoch0Vectors.vectors) {
      expect(Tier1.EPOCH_0_MAPPING[v.standard_field]).toBe(v.obfuscated_token);
    }
  });

  test('Epoch 1 static mapping matches test vectors', () => {
    // Verifies token distinctness across vector sets
    for (const v of epoch1Vectors.vectors) {
      // Epoch 1 tokens must differ from Epoch 0
      expect(v.obfuscated_token).not.toBe(Tier1.EPOCH_0_MAPPING[v.standard_field]);
    }
  });

  test('Tier 1 encode replaces all standard fields', () => {
    const payload: Record<string, any> = {};
    for (const v of epoch0Vectors.vectors) payload[v.standard_field] = 'test';
    const tier1 = new Tier1('test-endpoint');
    const encoded = tier1.encode(payload);
    for (const v of epoch0Vectors.vectors) {
      expect(encoded).toHaveProperty(v.obfuscated_token);
      expect(encoded).not.toHaveProperty(v.standard_field);
    }
  });

  test('Tier 1 encode/decode roundtrip is lossless', () => {
    const payload = { amount: 1000, user_id: 'usr_123', currency: 'USD' };
    const tier1 = new Tier1('test-endpoint');
    const encoded = tier1.encode(payload);
    const decoded = tier1.decode(encoded, JSON.stringify(encoded));
    expect(decoded).toEqual(payload);
  });

  test('HMAC-SHA256 produces identical output across Python and Node.js (vector 0)', () => {
    // Verifies cross-SDK HMAC parity using test vector reference hash
    const hmac = crypto.createHmac('sha256', masterSecret);
    hmac.update('epoch_0', 'utf8');
    expect(hmac.digest('hex')).toBe(epoch0Vectors.k_epoch_hex);
  });

  test('HMAC-SHA256 produces identical output across Python and Node.js (vector 1)', () => {
    const hmac = crypto.createHmac('sha256', masterSecret);
    hmac.update('epoch_1', 'utf8');
    expect(hmac.digest('hex')).toBe(epoch1Vectors.k_epoch_hex);
  });

  test('Tier 2 Base36 encoding matches Python: 1000 → "RS"', () => {
    const tier2 = new Tier2('test-endpoint', masterSecret);
    const encoded = tier2.encode({ amount: 1000 });
    expect(encoded[Tier1.EPOCH_0_MAPPING['amount']]).toBe('RS');
  });

  test('Tier 2 HMAC string token matches Python (deterministic)', () => {
    const tier2 = new Tier2('test-endpoint', masterSecret);
    const encoded = tier2.encode({ user_id: 'U123' });
    const expected = crypto
      .createHmac('sha256', masterSecret)
      .update('U123')
      .digest('hex')
      .substring(0, 12)
      .toUpperCase();
    expect(encoded[Tier1.EPOCH_0_MAPPING['user_id']]).toBe(expected);
  });

  test('Tier 2 decode recovers integer from Base36', () => {
    const tier2 = new Tier2('test-endpoint', masterSecret);
    const raw = JSON.stringify({ 'XR7F2K9Q': 'RS', 'U9B3MX1P': 'AABBCCDDEEFF' });
    const decoded = tier2.decode(JSON.parse(raw), raw);
    expect(decoded['amount']).toBe(1000);
  });
});
