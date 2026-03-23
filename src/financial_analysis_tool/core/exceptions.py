class ApplicationError(Exception):
    """Base application exception."""


class InputDataError(ApplicationError):
    """Raised when local input data is missing or malformed."""


class BinanceAPIError(ApplicationError):
    """Raised when the Binance exchange request fails."""
