class ApplicationError(Exception):
    """Base application exception."""


class InputDataError(ApplicationError):
    """Raised when local input data is missing or malformed."""


class BinanceAPIError(ApplicationError):
    """Raised when the Binance exchange request fails."""


class MOPSAPIError(ApplicationError):
    """Raised when the MOPS financial statement request fails."""


class TWSEAPIError(ApplicationError):
    """Raised when the TWSE market data request fails."""


class TEJAPIError(ApplicationError):
    """Raised when the TEJ market data request fails."""
