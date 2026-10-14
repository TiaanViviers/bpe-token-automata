"""Errors for string-to-tokenization transducers."""


class TransducerError(ValueError):
    """Raised when a transducer is malformed or determinisation fails."""


class TokenizationError(ValueError):
    """Raised when the input is outside the transducer's domain."""
