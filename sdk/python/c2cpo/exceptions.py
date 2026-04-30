class C2CPOBaseError(Exception):
    """Base class for all C2CPO SDK exceptions."""
    pass


class C2CPOFormatViolationError(C2CPOBaseError):
    """
    Raised when a payload contains unencoded standard field names.

    This indicates either a misconfigured producer (forgot to encode)
    or an attacker sending standard REST requests. Always fail-closed:
    the payload is rejected and a FORMAT_VIOLATION event is emitted.
    """
    pass


class C2CPOEncoderError(C2CPOBaseError):
    """Raised when the encoder fails due to an internal error."""
    pass
