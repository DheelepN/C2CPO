/** Base class for all C2CPO SDK errors. */
export class C2CPOBaseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'C2CPOBaseError';
  }
}

/**
 * Raised when a payload contains unencoded standard field names.
 *
 * Indicates either a misconfigured producer or an attacker sending
 * standard REST requests. Always fail-closed.
 */
export class C2CPOFormatViolationError extends C2CPOBaseError {
  constructor(message: string) {
    super(message);
    this.name = 'C2CPOFormatViolationError';
  }
}

/** Raised when the encoder fails due to an internal error. */
export class C2CPOEncoderError extends C2CPOBaseError {
  constructor(message: string) {
    super(message);
    this.name = 'C2CPOEncoderError';
  }
}
