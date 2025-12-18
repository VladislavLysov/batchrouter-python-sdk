"""Exception classes for BatchRouter SDK."""


class BatchRouterError(Exception):
    """Base exception for all BatchRouter errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(BatchRouterError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class NotFoundError(BatchRouterError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(BatchRouterError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class ServerError(BatchRouterError):
    """Raised when the server returns an error."""

    def __init__(self, message: str = "Server error"):
        super().__init__(message, status_code=500)
